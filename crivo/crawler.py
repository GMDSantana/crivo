"""

╔██████╗██████╗ ██╗██╗     ██╗╔██████╗
██╔════╝██╔══██╗██║╚██╗   ██╔╝██╔═══██╗
██║     ██████╔╝██║ ╚██╗ ██╔╝ ██║   ██║
██║     ██╔██═╝ ██║  ╚████╔╝  ██║   ██╝
╚██████╗██║ ██╗ ██║   ╚██╔╝   ╚██████╝
© Guilherme Santana
https://gmdsantana.com
https://github.com/GMDSantana/crivo

"""

# Breadth-first crawling with depth control (issue #12).
#
# Depth 0 disables crawling. At depth 1 Crivo also fetches the URLs found in
# the initial input (the links of a webpage given with -w/-W, or the URLs in
# a file or standard input); at depth 2 it follows the links on those pages,
# and so on. Only in-scope URLs are fetched at every level, including
# redirect targets:
#
# * with scope targets (-s example.com, -s 10.0.0.0/8, -s keyword), a URL is
#   followed only if it matches them;
# * without scope targets, Crivo stays on the starting site: the starting
#   hosts (without a leading "www.") and their subdomains.
#
# The number of pages fetched per crawl is capped by max_pages.

import logging
from collections import deque
from dataclasses import dataclass, field
from urllib.parse import urlsplit, urlunsplit

from crivo.filter_engine import URL, ScopeMatcher, extract_urls
from crivo.web_scraper import RedirectBlockedError, extract_links

logger = logging.getLogger("crivo")

DEFAULT_MAX_PAGES = 100

# Links to files that are not worth fetching (they are still reported as
# results when they appear in a page).
SKIPPED_EXTENSIONS = frozenset({
    # images
    ".apng", ".avif", ".bmp", ".gif", ".ico", ".jpeg", ".jpg", ".png", ".svg", ".tif", ".tiff", ".webp",
    # fonts and styles
    ".css", ".eot", ".otf", ".ttf", ".woff", ".woff2",
    # audio and video
    ".avi", ".flac", ".m4a", ".mkv", ".mov", ".mp3", ".mp4", ".mpeg", ".ogg", ".wav", ".webm",
    # documents, archives and binaries
    ".7z", ".apk", ".bin", ".bz2", ".deb", ".dmg", ".doc", ".docx", ".exe", ".gz", ".iso", ".jar",
    ".msi", ".pdf", ".ppt", ".pptx", ".rar", ".rpm", ".tar", ".tgz", ".xls", ".xlsx", ".xz", ".zip",
})


def normalise_crawl_url(url):
    """
    Normalises an http(s) URL for crawling, or returns None if it cannot be crawled.

    The fragment is removed, the scheme and host are lower-cased, default
    ports are dropped and an empty path becomes "/", so that equivalent URLs
    are fetched only once.
    """
    try:
        parts = urlsplit(url.strip())
        hostname = parts.hostname
        port = parts.port
    except (ValueError, AttributeError):
        return None
    scheme = parts.scheme.lower()
    if scheme not in ("http", "https") or not hostname:
        return None

    host = f"[{hostname}]" if ":" in hostname else hostname
    if port is not None and port != {"http": 80, "https": 443}[scheme]:
        host = f"{host}:{port}"
    userinfo = parts.netloc.rpartition("@")[0]
    netloc = f"{userinfo}@{host}" if userinfo else host
    return urlunsplit((scheme, netloc, parts.path or "/", parts.query, ""))


def has_skipped_extension(url):
    """Tells whether the URL path ends in an extension listed in SKIPPED_EXTENSIONS."""
    path = urlsplit(url).path.lower()
    name = path.rsplit("/", 1)[-1]
    dot = name.rfind(".")
    return dot != -1 and name[dot:] in SKIPPED_EXTENSIONS


def site_base(host):
    """The host without a leading "www.", used to define the starting site."""
    host = (host or "").lower().rstrip(".")
    return host[4:] if host.startswith("www.") and host.count(".") >= 2 else host


def page_links(page):
    """
    Returns the crawlable links of a fetched page, in order of appearance.

    These are the href/src/action attribute values (resolved against the
    page URL) followed by the absolute http(s) URLs found in the text.
    """
    links = []
    seen = set()
    for link in [*extract_links(page.text, page.url), *sorted(extract_urls(page.text))]:
        key = normalise_crawl_url(link)
        if key and key not in seen and not has_skipped_extension(key):
            seen.add(key)
            links.append(key)
    return links


@dataclass
class CrawlResult:
    """Results and statistics of one crawl."""

    results: set = field(default_factory=set)
    fetched: int = 0  # pages requested, including failures
    failed: int = 0  # pages that could not be fetched
    skipped: int = 0  # non-text responses and redirects out of scope
    not_crawled: int = 0  # in-scope URLs left unvisited because max_pages was reached


_MISSING = object()


@dataclass
class _Page:
    url: str
    results: list
    links: list


class Crawler:
    """
    Crawls webpages breadth-first up to a maximum depth.

    Args:
        fetch (callable): fetch(url, allow_url=None, text_only=False) -> FetchResult.
            Must raise RuntimeError when a page cannot be fetched.
        analyse (callable): analyse(FetchResult) -> iterable of results for that page.
        max_depth (int): Maximum crawl depth; 0 disables crawling.
        max_pages (int): Maximum number of pages to request per crawl.
        scope (ScopeMatcher | None): Scope targets. When empty, crawling stays
            on the starting site.
    """

    def __init__(self, fetch, analyse, max_depth, max_pages=DEFAULT_MAX_PAGES, scope=None):
        if max_depth < 0:
            raise ValueError("max_depth must be 0 or more")
        if max_pages < 1:
            raise ValueError("max_pages must be 1 or more")
        self.fetch = fetch
        self.analyse = analyse
        self.max_depth = max_depth
        self.max_pages = max_pages
        self.scope = scope if scope is not None else ScopeMatcher([])
        # Pages already analysed in this run (shared by the crawls of a -W list).
        self._cache = {}

    def in_scope(self, url, site_hosts):
        """Tells whether the crawler may request url."""
        key = normalise_crawl_url(url)
        if key is None:
            return False
        if self.scope:
            return self.scope.matches(key, URL)
        host = urlsplit(key).hostname
        return any(host == base or host.endswith("." + base) for base in site_hosts)

    def _visit(self, url, site_hosts, crawl, explicit=False):
        """Fetches and analyses a page, using the cache. Returns a _Page or None."""
        cached = self._cache.get(url, _MISSING)
        # A page the user asked for is retried if it failed earlier as a crawled link,
        # so that its error is reported.
        if cached is not _MISSING and (cached is not None or not explicit):
            return cached

        crawl.fetched += 1
        try:
            if explicit:
                # A page the user asked for: redirects are followed as without crawling.
                page = self.fetch(url)
            else:
                page = self.fetch(url, allow_url=lambda target: self.in_scope(target, site_hosts), text_only=True)
        except RedirectBlockedError as exc:
            crawl.skipped += 1
            logger.info("Skipped: %s", exc)
            return None
        except RuntimeError as exc:
            if explicit:
                raise
            crawl.failed += 1
            logger.info("Could not crawl: %s", exc)
            self._cache[url] = None
            return None

        if page.skipped:
            crawl.skipped += 1
            logger.info("Skipped %s (Content-Type: %s)", url, page.content_type)
            visited = _Page(page.url, [], [])
        else:
            visited = _Page(page.url, list(self.analyse(page)), page_links(page))
        self._cache[url] = visited
        return visited

    def _run(self, frontier, site_hosts, crawl, explicit_first=False):
        queue = deque(frontier)
        seen = {url for url, _ in frontier}
        first = explicit_first
        while queue:
            url, depth = queue[0]
            if crawl.fetched >= self.max_pages and self._cache.get(url) is None:
                crawl.not_crawled = len(queue)
                break
            queue.popleft()
            logger.info("Crawling (depth %d): %s", depth, url)
            page = self._visit(url, site_hosts, crawl, explicit=first)
            if first and page is not None:
                # Redirects of the starting page (e.g. to "www.") belong to the site.
                final_host = urlsplit(page.url).hostname
                if final_host:
                    site_hosts.add(site_base(final_host))
            first = False
            if page is None:
                continue
            crawl.results.update(page.results)
            if depth >= self.max_depth:
                continue
            for link in page.links:
                if link not in seen and self.in_scope(link, site_hosts):
                    seen.add(link)
                    queue.append((link, depth + 1))
        return crawl

    def crawl_url(self, url):
        """
        Crawls from a webpage given by the user (-w or an entry of -W).

        The page itself is always fetched (depth 0); its links are depth 1.

        Raises:
            RuntimeError: If the starting page cannot be fetched.
        """
        start = normalise_crawl_url(url) or url
        site_hosts = {site_base(urlsplit(start).hostname or "")}
        return self._run([(start, 0)], site_hosts, CrawlResult(), explicit_first=True)

    def crawl_text(self, text):
        """
        Crawls from the URLs found in text (a file or standard input).

        Those URLs are depth 1. Without scope targets they are all fetched,
        and their hosts define the site for deeper levels.
        """
        crawl = CrawlResult()
        if self.max_depth < 1:
            return crawl
        urls = []
        for found in sorted(extract_urls(text)):
            key = normalise_crawl_url(found)
            if key and key not in urls and not has_skipped_extension(key):
                urls.append(key)
        site_hosts = {site_base(urlsplit(url).hostname) for url in urls}
        if self.scope:
            urls = [url for url in urls if self.in_scope(url, site_hosts)]
        return self._run([(url, 1) for url in urls], site_hosts, crawl)
