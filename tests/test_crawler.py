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

import pytest

from crivo.crawler import (
    Crawler,
    has_skipped_extension,
    normalise_crawl_url,
    page_links,
    site_base,
)
from crivo.filter_engine import ScopeMatcher, filter_content
from crivo.web_scraper import FetchResult, RedirectBlockedError

# --- Helpers --------------------------------------------------------------------


@pytest.mark.parametrize(
    "url, expected",
    [
        ("https://Example.COM", "https://example.com/"),
        ("http://example.com:80/a#frag", "http://example.com/a"),
        ("https://example.com:443/?q=1", "https://example.com/?q=1"),
        ("https://example.com:8443/x", "https://example.com:8443/x"),
        ("HTTP://[2001:DB8::1]:8080/p", "http://[2001:db8::1]:8080/p"),
        ("https://User:Pw@Example.com/", "https://User:Pw@example.com/"),
        ("  https://example.com/a?b=C  ", "https://example.com/a?b=C"),
        ("ftp://example.com/", None),
        ("mailto:x@example.com", None),
        ("https://", None),
        ("http://example.com:notaport/", None),
        ("http://[::1/", None),
    ],
)
def test_normalise_crawl_url(url, expected):
    assert normalise_crawl_url(url) == expected


@pytest.mark.parametrize(
    "url, expected",
    [
        ("https://example.com/logo.PNG", True),
        ("https://example.com/report.pdf?download=1", True),
        ("https://example.com/style.css", True),
        ("https://example.com/app.js", False),  # scripts often contain endpoints
        ("https://example.com/page.html", False),
        ("https://example.com/dir.png/", False),
        ("https://example.com/", False),
    ],
)
def test_has_skipped_extension(url, expected):
    assert has_skipped_extension(url) is expected


@pytest.mark.parametrize(
    "host, expected",
    [("www.example.com", "example.com"), ("example.com", "example.com"), ("WWW.Example.com.", "example.com"),
     ("www.com", "www.com"), ("blog.example.com", "blog.example.com"), ("127.0.0.1", "127.0.0.1")],
)
def test_site_base(host, expected):
    assert site_base(host) == expected


def test_page_links_order_dedupe_and_skips():
    page = FetchResult(
        url="https://example.com/dir/",
        text='<a href="a">a</a> <a href="/dir/a#x">dup</a> <img src="i.png"> '
             '<a href="mailto:m@example.com">m</a> text https://other.org/p and https://example.com/dir/a',
    )
    assert page_links(page) == ["https://example.com/dir/a", "https://other.org/p"]


# --- Crawler with an in-memory web --------------------------------------------


class FakeWeb:
    """Serves pages from a dict and records every request."""

    def __init__(self, pages, redirects=None, failing=(), binary=()):
        self.pages = pages
        self.redirects = redirects or {}
        self.failing = set(failing)
        self.binary = set(binary)
        self.requests = []

    def fetch(self, url, allow_url=None, text_only=False):
        self.requests.append(url)
        if url in self.redirects:
            target = self.redirects[url]
            if allow_url is not None and not allow_url(target):
                raise RedirectBlockedError(f"Error fetching the webpage '{url}': redirect to '{target}' is out of scope.")
            self.requests.append(target)
            url = target
        if url in self.failing or url not in self.pages:
            raise RuntimeError(f"Error fetching the webpage '{url}': 404")
        if text_only and url in self.binary:
            return FetchResult(url=url, text="", content_type="application/octet-stream", skipped=True)
        return FetchResult(url=url, text=self.pages[url], content_type="text/html")


def analyse_ipv4(page):
    return filter_content(page.text, filter_ipv4=True)


SITE = {
    "https://example.com/": 'home 10.0.0.1 <a href="/a">a</a> <a href="/b">b</a> '
                            '<a href="https://other.org/">other</a> <a href="https://blog.example.com/">blog</a>',
    "https://example.com/a": 'a 10.0.0.2 <a href="/a/deep">deep</a> <a href="/">home</a>',
    "https://example.com/a/deep": "deep 10.0.0.3",
    "https://example.com/b": 'b 10.0.0.4 <a href="/a">a</a>',
    "https://blog.example.com/": "blog 10.0.0.5",
    "https://other.org/": "other 10.0.0.6",
}


def make_crawler(web, depth, max_pages=100, scope=()):
    return Crawler(web.fetch, analyse_ipv4, depth, max_pages, ScopeMatcher(list(scope)))


def test_depth_zero_fetches_only_the_start_page():
    web = FakeWeb(SITE)
    crawl = make_crawler(web, 0).crawl_url("https://example.com/")
    assert crawl.results == {"10.0.0.1"}
    assert web.requests == ["https://example.com/"]


@pytest.mark.parametrize(
    "depth, expected",
    [
        (1, {"10.0.0.1", "10.0.0.2", "10.0.0.4", "10.0.0.5"}),
        (2, {"10.0.0.1", "10.0.0.2", "10.0.0.3", "10.0.0.4", "10.0.0.5"}),
        (5, {"10.0.0.1", "10.0.0.2", "10.0.0.3", "10.0.0.4", "10.0.0.5"}),
    ],
)
def test_depth_limits_and_same_site_default(depth, expected):
    web = FakeWeb(SITE)
    crawl = make_crawler(web, depth).crawl_url("https://example.com/")
    assert crawl.results == expected  # other.org (10.0.0.6) is never fetched
    assert "https://other.org/" not in web.requests


def test_each_page_is_fetched_once_despite_loops():
    web = FakeWeb(SITE)
    crawl = make_crawler(web, 10).crawl_url("https://example.com/")
    assert len(web.requests) == len(set(web.requests)) == 5
    assert crawl.fetched == 5


def test_breadth_first_order():
    web = FakeWeb(SITE)
    make_crawler(web, 2).crawl_url("https://example.com/")
    assert web.requests == [
        "https://example.com/",
        "https://example.com/a",
        "https://example.com/b",
        "https://blog.example.com/",
        "https://example.com/a/deep",
    ]


def test_scope_targets_replace_the_same_site_default():
    web = FakeWeb(SITE)
    crawl = make_crawler(web, 1, scope=["other.org"]).crawl_url("https://example.com/")
    # The start page is always fetched; only in-scope links are followed.
    assert web.requests == ["https://example.com/", "https://other.org/"]
    assert crawl.results == {"10.0.0.1", "10.0.0.6"}


def test_scope_is_enforced_at_every_level():
    pages = {
        "https://example.com/": '<a href="https://example.com/in">in</a> 10.0.0.1',
        "https://example.com/in": '<a href="https://evil.net/">out</a> <a href="https://x.example.com/">sub</a> 10.0.0.2',
        "https://x.example.com/": "10.0.0.3",
        "https://evil.net/": "10.0.0.4",
    }
    web = FakeWeb(pages)
    crawl = make_crawler(web, 5, scope=["example.com"]).crawl_url("https://example.com/")
    assert crawl.results == {"10.0.0.1", "10.0.0.2", "10.0.0.3"}
    assert "https://evil.net/" not in web.requests


def test_out_of_scope_redirects_are_not_followed():
    pages = dict(SITE, **{"https://example.com/": '<a href="/go">go</a> 10.0.0.1'})
    web = FakeWeb(pages, redirects={"https://example.com/go": "https://other.org/"})
    crawl = make_crawler(web, 1).crawl_url("https://example.com/")
    assert crawl.results == {"10.0.0.1"}
    assert crawl.skipped == 1
    assert "https://other.org/" not in web.requests


def test_start_page_redirect_to_www_extends_the_site():
    pages = {
        "https://www.example.com/": '<a href="/x">x</a> <a href="https://shop.example.com/">shop</a> '
                                    '<a href="https://other.org/">o</a> 10.0.0.1',
        "https://www.example.com/x": "10.0.0.2",
        "https://shop.example.com/": "10.0.0.3",
        "https://other.org/": "10.0.0.4",
    }
    web = FakeWeb(pages, redirects={"https://example.com/": "https://www.example.com/"})
    crawl = make_crawler(web, 1).crawl_url("https://example.com")
    assert crawl.results == {"10.0.0.1", "10.0.0.2", "10.0.0.3"}


def test_max_pages_caps_requests_and_reports_the_rest():
    web = FakeWeb(SITE)
    crawl = make_crawler(web, 5, max_pages=2).crawl_url("https://example.com/")
    assert web.requests == ["https://example.com/", "https://example.com/a"]
    assert crawl.fetched == 2
    assert crawl.not_crawled == 3  # /b, the blog and /a/deep were queued but not fetched
    assert crawl.results == {"10.0.0.1", "10.0.0.2"}


def test_failed_and_skipped_pages_are_counted():
    pages = {"https://example.com/": '<a href="/gone">x</a> <a href="/file">y</a> 10.0.0.1',
             "https://example.com/file": "10.0.0.9"}
    web = FakeWeb(pages, binary={"https://example.com/file"})
    crawl = make_crawler(web, 1).crawl_url("https://example.com/")
    assert crawl.results == {"10.0.0.1"}
    assert (crawl.fetched, crawl.failed, crawl.skipped) == (3, 1, 1)


def test_start_page_failure_is_raised():
    web = FakeWeb({})
    with pytest.raises(RuntimeError, match="404"):
        make_crawler(web, 2).crawl_url("https://example.com/")


def test_pages_are_cached_between_crawls():
    web = FakeWeb(SITE)
    crawler = make_crawler(web, 1)
    crawler.crawl_url("https://example.com/a")
    first = list(web.requests)
    crawl = crawler.crawl_url("https://example.com/b")
    assert web.requests[len(first):] == ["https://example.com/b"]  # /a comes from the cache
    assert crawl.results == {"10.0.0.4", "10.0.0.2"}


def test_explicit_page_that_failed_as_a_link_is_retried():
    pages = {"https://example.com/": '<a href="/flaky">x</a> 10.0.0.1'}
    web = FakeWeb(pages, failing={"https://example.com/flaky"})
    crawler = make_crawler(web, 1)
    crawler.crawl_url("https://example.com/")
    with pytest.raises(RuntimeError):
        crawler.crawl_url("https://example.com/flaky")
    assert web.requests.count("https://example.com/flaky") == 2


def test_crawl_text_uses_urls_in_the_text():
    web = FakeWeb(SITE)
    text = "seeds: https://example.com/a and https://other.org/ and https://example.com/pic.jpg"
    crawl = make_crawler(web, 1).crawl_text(text)
    assert sorted(web.requests) == ["https://example.com/a", "https://other.org/"]
    assert crawl.results == {"10.0.0.2", "10.0.0.6"}


def test_crawl_text_deeper_levels_stay_on_the_seed_sites():
    web = FakeWeb(SITE)
    crawl = make_crawler(web, 2).crawl_text("https://example.com/a")
    assert crawl.results == {"10.0.0.1", "10.0.0.2", "10.0.0.3"}


def test_crawl_text_applies_scope_to_seed_urls():
    web = FakeWeb(SITE)
    crawl = make_crawler(web, 1, scope=["other.org"]).crawl_text("https://example.com/a https://other.org/")
    assert web.requests == ["https://other.org/"]
    assert crawl.results == {"10.0.0.6"}


def test_crawl_text_with_depth_zero_does_nothing():
    web = FakeWeb(SITE)
    assert make_crawler(web, 0).crawl_text("https://example.com/").fetched == 0
    assert web.requests == []


@pytest.mark.parametrize("depth, pages", [(-1, 10), (1, 0)])
def test_invalid_limits(depth, pages):
    with pytest.raises(ValueError):
        Crawler(lambda url: None, analyse_ipv4, depth, pages)
