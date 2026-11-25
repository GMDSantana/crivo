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

import uuid

import pytest
import requests

from crivo.web_scraper import (
    DEFAULT_TIMEOUT,
    DEFAULT_USER_AGENT,
    RedirectBlockedError,
    create_session,
    extract_links,
    fetch_webpage,
    is_text_content_type,
    normalise_url,
    scrape_webpage,
)

# --- Tests with a mocked session (adapted from Crivo 1.x) -------------------


def _mock_response(mocker, text="", status_error=None, url="http://example.com", content_type="text/html; charset=utf-8"):
    response = mocker.MagicMock()
    response.__enter__.return_value = response
    response.__exit__.return_value = False
    response.url = url
    response.headers = {"Content-Type": content_type}
    response.iter_content.return_value = [text.encode("utf-8")]
    if status_error is not None:
        response.raise_for_status.side_effect = status_error
    return response


def test_scrape_webpage_valid(mocker):
    response = _mock_response(mocker, "<html><body>Test content</body></html>")
    mocker.patch("requests.Session.get", return_value=response)

    content = scrape_webpage("http://example.com")
    assert content == "<html><body>Test content</body></html>"


def test_scrape_webpage_http_error(mocker):
    response = _mock_response(mocker, status_error=requests.exceptions.HTTPError("HTTP error"))
    mocker.patch("requests.Session.get", return_value=response)

    with pytest.raises(RuntimeError, match="Error fetching the webpage 'http://example.com': HTTP error"):
        scrape_webpage("http://example.com")


def test_scrape_webpage_request_exception(mocker):
    mocker.patch("requests.Session.get", side_effect=requests.exceptions.RequestException("Request failed"))

    with pytest.raises(RuntimeError, match="Error fetching the webpage 'http://example.com': Request failed"):
        scrape_webpage("http://example.com")


def test_scrape_webpage_connection_error(mocker):
    mocker.patch("requests.Session.get", side_effect=requests.ConnectionError("Connection failed"))

    with pytest.raises(RuntimeError, match="Error fetching the webpage"):
        scrape_webpage("http://example.com")


def test_fetch_uses_timeout_and_streaming(mocker):
    # Regression: 1.x called requests.get() without a timeout and could hang forever.
    get = mocker.patch("requests.Session.get", return_value=_mock_response(mocker, "ok"))
    fetch_webpage("http://example.com")
    kwargs = get.call_args.kwargs
    assert kwargs["timeout"] == DEFAULT_TIMEOUT
    assert kwargs["stream"] is True
    assert kwargs["verify"] is True


def test_fetch_can_disable_tls_verification(mocker):
    get = mocker.patch("requests.Session.get", return_value=_mock_response(mocker, "ok"))
    fetch_webpage("https://example.com", verify=False, timeout=3)
    assert get.call_args.kwargs["verify"] is False
    assert get.call_args.kwargs["timeout"] == 3


def test_given_session_is_not_closed(mocker):
    session = create_session()
    mocker.patch.object(session, "get", return_value=_mock_response(mocker, "ok"))
    close = mocker.patch.object(session, "close")
    fetch_webpage("http://example.com", session=session)
    close.assert_not_called()


# --- URL normalisation -------------------------------------------------------


@pytest.mark.parametrize(
    "url, expected",
    [
        ("https://example.com", "https://example.com"),
        ("  http://example.com/x  ", "http://example.com/x"),
        ("example.com", "https://example.com"),
        ("example.com:8443/path", "https://example.com:8443/path"),
        ("//cdn.example.com/lib.js", "https://cdn.example.com/lib.js"),
        ("HTTP://EXAMPLE.COM", "HTTP://EXAMPLE.COM"),
    ],
)
def test_normalise_url(url, expected):
    assert normalise_url(url) == expected


@pytest.mark.parametrize(
    "url, message",
    [
        ("", "empty"),
        ("   ", "empty"),
        ("ftp://example.com", "Unsupported URL scheme"),
        ("file:///etc/passwd", "Unsupported URL scheme"),
        ("https://", "no host"),
        ("http://[::1", "Invalid URL"),
    ],
)
def test_normalise_url_rejects_bad_urls(url, message):
    with pytest.raises(ValueError, match=message):
        normalise_url(url)


def test_fetch_reports_invalid_url_as_runtime_error():
    with pytest.raises(RuntimeError, match="Unsupported URL scheme"):
        fetch_webpage("ftp://example.com")


# --- Session -----------------------------------------------------------------


def test_session_sets_user_agent_and_retries():
    session = create_session(retries=3)
    assert session.headers["User-Agent"] == DEFAULT_USER_AGENT
    retry = session.get_adapter("https://example.com").max_retries
    assert retry.total == 3
    assert 503 in retry.status_forcelist
    assert retry.respect_retry_after_header is False


# --- Link extraction ---------------------------------------------------------


def test_extract_links_resolves_and_filters():
    html = """
    <a href="/about">x</a> <a href='https://other.org/p?a=1&amp;b=2'>y</a>
    <img src=img/logo.png> <form action="login"></form>
    <a href="#top">t</a> <a href="javascript:void(0)">j</a> <a href="mailto:a@b.com">m</a>
    <a href="data:text/plain,hi">d</a> <a href="TEL:123">p</a> <a href="">e</a>
    <a href="/about">duplicate</a>
    """
    assert extract_links(html, "https://example.com/dir/page.html") == [
        "https://example.com/about",
        "https://other.org/p?a=1&b=2",
        "https://example.com/dir/img/logo.png",
        "https://example.com/dir/login",
    ]


def test_scrape_webpage_resolve_links(mocker):
    response = _mock_response(mocker, '<a href="/a">a</a>', url="https://example.com/start")
    mocker.patch("requests.Session.get", return_value=response)
    assert scrape_webpage("https://example.com/start", resolve_links=True) == "https://example.com/a"


# --- End-to-end tests against a local HTTP server ----------------------------


def test_fetch_page(http_server):
    page = fetch_webpage(f"{http_server}/page")
    assert page.url == f"{http_server}/page"
    assert "Café ☕" in page.text  # UTF-8 from <meta charset>, not mangled as Latin-1
    assert page.truncated is False


def test_fetch_follows_redirects_and_reports_final_url(http_server):
    page = fetch_webpage(f"{http_server}/redirect")
    assert page.url == f"{http_server}/page"
    links = extract_links(page.text, page.url)
    assert f"{http_server}/about" in links
    assert f"{http_server}/img/logo.png" in links


def test_fetch_declared_charset(http_server):
    assert "süd.example.com" in fetch_webpage(f"{http_server}/latin1").text


def test_fetch_without_charset_falls_back_to_utf8(http_server):
    assert "açaí.example.com" in fetch_webpage(f"{http_server}/nocharset").text


def test_fetch_http_error(http_server):
    with pytest.raises(RuntimeError, match="404"):
        fetch_webpage(f"{http_server}/notfound")


def test_fetch_retries_transient_errors(http_server):
    key = uuid.uuid4().hex
    page = fetch_webpage(f"{http_server}/flaky?key={key}&fail=1")
    assert "recovered" in page.text


def test_fetch_gives_up_after_retries(http_server):
    key = uuid.uuid4().hex
    session = create_session(retries=0)
    with pytest.raises(RuntimeError, match="503"):
        fetch_webpage(f"{http_server}/flaky?key={key}&fail=5", session=session)


def test_fetch_timeout(http_server):
    session = create_session(retries=0)
    with pytest.raises(RuntimeError, match="Error fetching the webpage"):
        fetch_webpage(f"{http_server}/slow?delay=2", timeout=0.3, session=session)


def test_fetch_truncates_large_bodies(http_server, caplog):
    page = fetch_webpage(f"{http_server}/big?size=500000", max_bytes=1000)
    assert len(page.text) == 1000
    assert page.truncated is True
    assert page.text.startswith("203.0.113.5 ")
    assert "truncated" in caplog.text


def test_fetch_connection_refused():
    # Port 9 (discard) on localhost is almost never listening.
    session = create_session(retries=0)
    with pytest.raises(RuntimeError, match="Error fetching the webpage"):
        fetch_webpage("http://127.0.0.1:9/", timeout=2, session=session)


# --- Fetch options used by the crawler ---------------------------------------


@pytest.mark.parametrize(
    "content_type, expected",
    [
        ("text/html; charset=utf-8", True),
        ("text/plain", True),
        ("application/json", True),
        ("application/javascript", True),
        ("application/ld+json", True),
        ("image/svg+xml", True),
        ("", True),
        (None, True),
        ("image/png", False),
        ("application/pdf", False),
        ("application/octet-stream", False),
        ("video/mp4", False),
    ],
)
def test_is_text_content_type(content_type, expected):
    assert is_text_content_type(content_type) is expected


def test_text_only_skips_binary_responses(http_server):
    page = fetch_webpage(f"{http_server}/site/binary", text_only=True)
    assert page.skipped is True
    assert page.text == ""
    assert page.content_type == "application/octet-stream"


def test_binary_responses_are_read_without_text_only(http_server):
    page = fetch_webpage(f"{http_server}/site/binary")
    assert page.skipped is False
    assert "127.1.0.97" in page.text


def test_allow_url_follows_allowed_redirects(http_server):
    page = fetch_webpage(f"{http_server}/site/redirect-in", allow_url=lambda url: url.startswith(http_server))
    assert page.url == f"{http_server}/site/c"
    assert "127.1.0.6" in page.text


def test_allow_url_blocks_redirects_before_requesting_them(http_server, http_hits):
    before = http_hits["/site/secret"]
    with pytest.raises(RedirectBlockedError, match="out of scope"):
        fetch_webpage(f"{http_server}/site/redirect-out", allow_url=lambda url: url.startswith(http_server))
    assert http_hits["/site/secret"] == before


def test_redirect_loop_is_reported(http_server):
    with pytest.raises(RuntimeError, match="more than 10 redirects"):
        fetch_webpage(f"{http_server}/site/loop", allow_url=lambda url: True)
