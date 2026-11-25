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

import codecs
import html
import logging
import re
from dataclasses import dataclass
from urllib.parse import urljoin, urlsplit

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from crivo.version import __version__

logger = logging.getLogger("crivo")

DEFAULT_TIMEOUT = 15.0  # seconds, for both connecting and reading
DEFAULT_RETRIES = 2
DEFAULT_MAX_BYTES = 10 * 1024 * 1024  # 10 MiB
DEFAULT_USER_AGENT = f"Crivo/{__version__} (+https://github.com/GMDSantana/crivo)"

_RETRY_STATUSES = (429, 500, 502, 503, 504)
_CHUNK_SIZE = 64 * 1024

_CHARSET_HEADER_RE = re.compile(r"charset\s*=\s*[\"']?([\w.:-]+)", re.IGNORECASE)
_CHARSET_META_RE = re.compile(rb"<meta[^>]+charset\s*=\s*[\"']?([\w.:-]+)", re.IGNORECASE)
_LINK_RE = re.compile(
    r"""\b(?:href|src|action)\s*=\s*(?:"([^"]*)"|'([^']*)'|([^\s"'<>`=]+))""",
    re.IGNORECASE,
)
_SKIPPED_LINK_SCHEMES = ("javascript:", "mailto:", "data:", "tel:", "about:", "blob:")
_REDIRECT_STATUSES = (301, 302, 303, 307, 308)
MAX_REDIRECTS = 10
_TEXT_MIME_TYPES = frozenset({
    "application/json",
    "application/javascript",
    "application/ecmascript",
    "application/x-javascript",
    "application/xml",
    "application/xhtml+xml",
})


class RedirectBlockedError(RuntimeError):
    """Raised when a redirect would leave the allowed scope."""


@dataclass(frozen=True)
class FetchResult:
    """The outcome of fetching a webpage."""

    url: str  # final URL, after redirects
    text: str
    truncated: bool = False
    content_type: str = ""
    skipped: bool = False  # True if the body was not read because it is not text


def is_text_content_type(content_type):
    """
    Tells whether a Content-Type header describes text worth filtering.

    A missing Content-Type is treated as text.
    """
    mime = (content_type or "").split(";", 1)[0].strip().lower()
    if not mime:
        return True
    return mime.startswith("text/") or mime in _TEXT_MIME_TYPES or mime.endswith(("+json", "+xml"))


def normalise_url(url):
    """
    Validates a webpage URL, adding "https://" when no scheme is given.

    Args:
        url (str): The URL, e.g. "https://example.com" or "example.com/path".

    Returns:
        str: The URL with a scheme.

    Raises:
        ValueError: If the URL is empty, has no host or does not use http(s).
    """
    url = (url or "").strip()
    if not url:
        raise ValueError("The URL is empty.")
    if not re.match(r"^[a-z][a-z0-9+.-]*://", url, re.IGNORECASE):
        url = "https://" + url.lstrip("/")
    try:
        parts = urlsplit(url)
        hostname = parts.hostname
    except ValueError as exc:
        raise ValueError(f"Invalid URL '{url}': {exc}") from None
    if parts.scheme.lower() not in ("http", "https"):
        raise ValueError(f"Unsupported URL scheme '{parts.scheme}' in '{url}'; only http and https are supported.")
    if not hostname:
        raise ValueError(f"The URL '{url}' has no host.")
    return url


def create_session(retries=DEFAULT_RETRIES, user_agent=DEFAULT_USER_AGENT):
    """
    Creates a requests session that retries transient failures.

    Connection errors and 429/5xx responses are retried with a short
    exponential back-off. Retry-After headers are ignored so that a server
    cannot stall Crivo for an arbitrary length of time.
    """
    session = requests.Session()
    retry = Retry(
        total=retries,
        connect=retries,
        read=retries,
        status=retries,
        backoff_factor=0.5,
        status_forcelist=_RETRY_STATUSES,
        respect_retry_after_header=False,
        raise_on_status=False,
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    session.headers["User-Agent"] = user_agent
    return session


def _read_limited(response, max_bytes):
    chunks = []
    size = 0
    for chunk in response.iter_content(chunk_size=_CHUNK_SIZE):
        if not chunk:
            continue
        if max_bytes is not None and size + len(chunk) > max_bytes:
            chunks.append(chunk[: max_bytes - size])
            return b"".join(chunks), True
        chunks.append(chunk)
        size += len(chunk)
    return b"".join(chunks), False


def _known_codec(name):
    if not name:
        return None
    try:
        return codecs.lookup(name).name
    except LookupError:
        return None


def _decode(body, content_type):
    """Decodes the body using the declared charset, a <meta> tag, UTF-8 or Latin-1."""
    match = _CHARSET_HEADER_RE.search(content_type or "")
    encoding = _known_codec(match.group(1)) if match else None
    if encoding is None:
        meta = _CHARSET_META_RE.search(body[:4096])
        encoding = _known_codec(meta.group(1).decode("ascii", "ignore")) if meta else None
    if encoding is not None:
        return body.decode(encoding, errors="replace")
    try:
        return body.decode("utf-8")
    except UnicodeDecodeError:
        return body.decode("latin-1")


def fetch_webpage(url, *, timeout=DEFAULT_TIMEOUT, verify=True, max_bytes=DEFAULT_MAX_BYTES, session=None,
                  allow_url=None, text_only=False):
    """
    Fetches a webpage and returns its decoded text.

    Args:
        url (str): The URL to fetch. "https://" is assumed when no scheme is given.
        timeout (float): Connect and read timeout in seconds.
        verify (bool): Whether to verify TLS certificates.
        max_bytes (int | None): Maximum body size to read; larger bodies are truncated.
        session (requests.Session | None): Session to use. A retrying session is
            created (and closed) when omitted.
        allow_url (callable | None): If given, redirects are followed one at a
            time and each target must satisfy allow_url(target) before it is
            requested, so a redirect can never reach an out-of-scope host.
        text_only (bool): If True, responses whose Content-Type is not text
            (images, archives, PDFs, ...) are not downloaded; an empty,
            skipped result is returned instead.

    Returns:
        FetchResult: The final URL, the text and whether it was truncated or skipped.

    Raises:
        RedirectBlockedError: If allow_url rejects a redirect target.
        RuntimeError: If the URL is invalid or the request fails.
    """
    try:
        url = normalise_url(url)
    except ValueError as exc:
        raise RuntimeError(f"Error fetching the webpage '{url}': {exc}") from None

    own_session = session is None
    if own_session:
        session = create_session()
    try:
        current = url
        for _ in range(MAX_REDIRECTS + 1):
            with session.get(current, timeout=timeout, verify=verify, stream=True,
                             allow_redirects=allow_url is None) as response:
                location = response.headers.get("Location")
                if allow_url is not None and response.status_code in _REDIRECT_STATUSES and location:
                    target = urljoin(current, location)
                    if not allow_url(target):
                        raise RedirectBlockedError(
                            f"Error fetching the webpage '{url}': redirect to '{target}' is out of scope."
                        )
                    current = target
                    continue
                response.raise_for_status()
                final_url = response.url or current
                content_type = response.headers.get("Content-Type") or ""
                if text_only and not is_text_content_type(content_type):
                    return FetchResult(url=final_url, text="", content_type=content_type, skipped=True)
                body, truncated = _read_limited(response, max_bytes)
                text = _decode(body, content_type)
                break
        else:
            raise RuntimeError(f"Error fetching the webpage '{url}': more than {MAX_REDIRECTS} redirects.")
    except requests.exceptions.RequestException as exc:
        raise RuntimeError(f"Error fetching the webpage '{url}': {exc}") from exc
    finally:
        if own_session:
            session.close()

    if truncated:
        logger.warning("Content from '%s' exceeded %d bytes and was truncated.", url, max_bytes)
    return FetchResult(url=final_url, text=text, truncated=truncated, content_type=content_type)


def extract_links(content, base_url):
    """
    Finds href, src and action attribute values and resolves them against base_url.

    Fragment-only links and javascript:, mailto:, data:, tel:, about: and
    blob: links are skipped. Duplicates are removed, keeping the first occurrence.

    Returns:
        list: Absolute links, in order of appearance.
    """
    links = []
    seen = set()
    for match in _LINK_RE.finditer(content):
        value = html.unescape(next(group for group in match.groups() if group is not None)).strip()
        if not value or value.startswith("#") or value.lower().startswith(_SKIPPED_LINK_SCHEMES):
            continue
        try:
            absolute = urljoin(base_url, value)
        except ValueError:
            continue
        if absolute not in seen:
            seen.add(absolute)
            links.append(absolute)
    return links


def scrape_webpage(url, resolve_links=False, **kwargs):
    """
    Fetches the content of a webpage and optionally resolves relative links.

    Args:
        url (str): The URL of the webpage to be scraped.
        resolve_links (bool): Whether to return only resolved links (default: False).
        **kwargs: Passed to fetch_webpage (timeout, verify, max_bytes, session).

    Returns:
        str: The full content of the webpage or resolved links if `resolve_links` is True.

    Raises:
        RuntimeError: If the webpage cannot be fetched.
    """
    result = fetch_webpage(url, **kwargs)
    if resolve_links:
        return "\n".join(extract_links(result.text, result.url))
    return result.text
