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

import time

import pytest

from crivo.filter_engine import (
    DEFAULT_TLD_FILE,
    ScopeMatcher,
    extract_domains,
    extract_ipv4,
    extract_ipv6,
    extract_urls,
    filter_content,
    load_valid_tlds,
    split_scope,
)

# --- Original Crivo 1.x tests -------------------------------------------------


def test_filter_content_no_filters():
    content = "192.168.0.1 example.com https://example.com"
    result = filter_content(content)
    expected = ["192.168.0.1", "example.com", "https://example.com"]
    assert sorted(result) == sorted(expected)


def test_filter_content_ipv4():
    content = "192.168.0.1 example.com https://example.com"
    result = filter_content(content, filter_ipv4=True)
    expected = ["192.168.0.1"]
    assert sorted(result) == sorted(expected)


def test_filter_content_domain():
    content = "192.168.0.1 example.com https://example.com"
    result = filter_content(content, filter_domain=True)
    expected = ["example.com"]
    assert sorted(result) == sorted(expected)


def test_filter_content_url():
    content = "Visit https://example.com and http://test.com for details."
    result = filter_content(content, filter_url=True)
    expected = ["https://example.com", "http://test.com"]
    assert sorted(result) == sorted(expected)


def test_filter_content_with_scope():
    content = "192.168.0.1 example.com https://example.com"
    result = filter_content(content, scope_filters=["example"])
    expected = ["example.com", "https://example.com"]
    assert sorted(result) == sorted(expected)


def test_filter_content_combined_filters():
    content = "192.168.0.1 example.com https://example.com"
    result = filter_content(content, filter_ip=True, filter_url=True)
    assert sorted(result) == ["192.168.0.1", "https://example.com"]


# --- TLD list -------------------------------------------------------------------


def test_bundled_tld_list_lives_in_the_package():
    assert DEFAULT_TLD_FILE.is_file()
    assert DEFAULT_TLD_FILE.parent.parent.name == "crivo"


def test_works_from_any_working_directory(tmp_path, monkeypatch):
    # Regression: 1.x opened 'valid_tlds.txt' relative to the current directory.
    monkeypatch.chdir(tmp_path)
    assert filter_content("see example.com") == ["example.com"]


def test_load_valid_tlds_skips_comments_and_adds_punycode(tmp_path):
    tld_file = tmp_path / "tlds.txt"
    tld_file.write_text("# Version 1\n\nCOM\n.net\n测试\n", encoding="utf-8")
    tlds = load_valid_tlds(tld_file)
    assert {"com", "net", "测试", "xn--0zwm56d"} <= tlds
    assert not any(t.startswith("#") for t in tlds)


def test_load_valid_tlds_missing_file(tmp_path):
    with pytest.raises(FileNotFoundError, match="was not found"):
        load_valid_tlds(tmp_path / "missing.txt")


def test_load_valid_tlds_empty_file(tmp_path):
    tld_file = tmp_path / "empty.txt"
    tld_file.write_text("# only a comment\n\n", encoding="utf-8")
    with pytest.raises(ValueError, match="empty"):
        load_valid_tlds(tld_file)


def test_custom_tlds_can_be_supplied():
    assert filter_content("a.internal b.com", tlds=frozenset({"internal"})) == ["a.internal"]


# --- IPv4 --------------------------------------------------------------------


@pytest.mark.parametrize(
    "text, expected",
    [
        ("host 10.0.0.1 up", {"10.0.0.1"}),
        ("edges 0.0.0.0 255.255.255.255", {"0.0.0.0", "255.255.255.255"}),
        ("invalid 999.999.999.999 256.1.1.1 300.1.1.1", set()),
        ("version 1.2.3.4.5", set()),  # part of a longer dotted number
        ("end of sentence 192.0.2.1.", {"192.0.2.1"}),
        ("in url http://198.51.100.2:8080/", {"198.51.100.2"}),
        ("comma 192.0.2.1,192.0.2.2", {"192.0.2.1", "192.0.2.2"}),
    ],
)
def test_extract_ipv4(text, expected):
    assert extract_ipv4(text) == expected


# --- IPv6 --------------------------------------------------------------------


@pytest.mark.parametrize(
    "text, expected",
    [
        ("full 2001:0db8:0000:0000:0000:ff00:0042:8329", {"2001:0db8:0000:0000:0000:ff00:0042:8329"}),
        ("compressed 2001:db8::1 and ::1", {"2001:db8::1", "::1"}),
        ("link-local fe80::1%eth0", {"fe80::1"}),
        ("mapped ::ffff:192.0.2.1", {"::ffff:192.0.2.1"}),
        ("bracketed [2001:db8::2]:443", {"2001:db8::2"}),
        ("prefix 2001:db8::/32", {"2001:db8::"}),
        ("upper 2001:DB8::A", {"2001:DB8::A"}),
        ("not ips 12:30:45 00:1a:2b:3c:4d:5e std::vector a :: b", set()),
        ("too many groups 1:2:3:4:5:6:7:8:9", set()),
        ("labelled ip:fe80::1 addr:2001:db8::7", {"fe80::1", "2001:db8::7"}),
    ],
)
def test_extract_ipv6(text, expected):
    assert extract_ipv6(text) == expected


def test_filter_ipv6_only():
    content = "192.0.2.1 2001:db8::1 example.com"
    assert filter_content(content, filter_ipv6=True) == ["2001:db8::1"]


def test_filter_ip_includes_both_versions():
    content = "192.0.2.1 2001:db8::1 example.com"
    assert filter_content(content, filter_ip=True) == ["192.0.2.1", "2001:db8::1"]


# --- URLs --------------------------------------------------------------------


@pytest.mark.parametrize(
    "text, expected",
    [
        ("plain https://example.com/path", {"https://example.com/path"}),
        ("keeps slash https://example.com/path/", {"https://example.com/path/"}),
        ("sentence https://example.com/a.", {"https://example.com/a"}),
        ("(see https://example.com/x)", {"https://example.com/x"}),
        ("wiki https://en.wikipedia.org/wiki/Foo_(bar).", {"https://en.wikipedia.org/wiki/Foo_(bar)"}),
        ("case HTTPS://EXAMPLE.COM/Path", {"https://example.com/Path"}),
        ("creds https://User:PaSs@Example.com/", {"https://User:PaSs@example.com/"}),
        ('html href="https://x.com/?a=1&amp;b=2"', {"https://x.com/?a=1&b=2"}),
        ("fragment https://example.com/page#section", {"https://example.com/page"}),
        ("query https://example.com/?q=1&r=2", {"https://example.com/?q=1&r=2"}),
        ("ipv6 http://[2001:db8::1]:8080/x", {"http://[2001:db8::1]:8080/x"}),
        ("port http://example.com:8080", {"http://example.com:8080"}),
        ("no host https:// and http://", set()),
        ("bad ipv6 http://[::1/x", set()),
        ("embedded xhttp://example.com", set()),
    ],
)
def test_extract_urls(text, expected):
    assert extract_urls(text) == expected


def test_json_escaped_urls_are_found():
    content = '{"next":"https:\\/\\/api.example.com\\/v1\\/items"}'
    assert filter_content(content, filter_url=True) == ["https://api.example.com/v1/items"]


# --- Domains -----------------------------------------------------------------


@pytest.mark.parametrize(
    "text, expected",
    [
        ("simple example.com", {"example.com"}),
        ("multi-level api.dev.example.co.uk", {"api.dev.example.co.uk"}),
        ("case Example.COM", {"example.com"}),
        ("hyphen foo-bar.example.com", {"foo-bar.example.com"}),
        ("email security@example.com", {"example.com"}),
        ("cookie domain .example.com;", {"example.com"}),
        ("dns _dmarc.example.com s1._domainkey.example.com", {"_dmarc.example.com", "s1._domainkey.example.com"}),
        ("unknown tld example.notatld", set()),
        ("trailing invalid label example.com.notatld", {"example.com"}),
        ("cjk 访问example.com获取", {"example.com"}),
        ("punycode tld example.xn--0zwm56d", {"example.xn--0zwm56d"}),
        ("unicode tld example.测试", {"example.测试"}),
        ("not ips 192.168.0.1", set()),
        ("email local part first.ninja@example.org", {"example.org"}),
        ("bad labels -bad-.example.com", {"example.com"}),
        ("accented word süd.example.com", set()),
        ("accented neighbour example.comé", set()),
        ("accented prose Olá example.com, até logo", {"example.com"}),
    ],
)
def test_extract_domains(text, expected):
    assert extract_domains(text) == expected


def test_domains_are_deduplicated_case_insensitively():
    assert filter_content("EXAMPLE.com example.COM", filter_domain=True) == ["example.com"]


def test_overlong_domain_is_rejected():
    domain = ".".join(["a" * 63] * 4) + ".com"  # 260 characters
    assert extract_domains(domain) == set()


# --- Scope -------------------------------------------------------------------


def test_scope_domain_matches_subdomains_not_lookalikes():
    content = "example.com a.example.com notexample.com example.com.evil.net https://b.example.com/x https://evil.net/?r=example.com"
    result = filter_content(content, scope_filters=["example.com"])
    assert result == ["a.example.com", "b.example.com", "example.com", "https://b.example.com/x"]


def test_scope_wildcard_and_url_entries():
    content = "a.example.com other.org"
    assert filter_content(content, scope_filters=["*.example.com"]) == ["a.example.com"]
    assert filter_content(content, scope_filters=["https://example.com/"]) == ["a.example.com"]


def test_scope_is_case_insensitive_and_strips_spaces():
    # Regression: 1.x did not strip spaces, so " test.com" never matched.
    content = "a.example.com test.com other.org"
    result = filter_content(content, scope_filters=["Example.COM", " test.com"])
    assert result == ["a.example.com", "test.com"]


def test_scope_string_is_split_on_commas():
    assert filter_content("a.example.com other.org", scope_filters="example.com, foo.net") == ["a.example.com"]


def test_scope_cidr_matches_ips_and_url_hosts():
    content = "10.0.0.5 10.0.1.5 http://10.0.0.6/x 2001:db8::1 a.example.com"
    assert filter_content(content, scope_filters=["10.0.0.0/24"]) == ["10.0.0.5", "10.0.0.6", "http://10.0.0.6/x"]
    assert filter_content(content, scope_filters=["2001:db8::/32"]) == ["2001:db8::1"]


def test_scope_single_ip():
    assert filter_content("10.0.0.5 10.0.0.6", scope_filters=["10.0.0.5"]) == ["10.0.0.5"]


def test_scope_keyword_matches_anywhere():
    content = "10.0.0.5 192.168.1.1 http://x.org/admin a.example.com"
    assert filter_content(content, scope_filters=["admin", "192.168."]) == ["192.168.1.1", "http://x.org/admin"]


@pytest.mark.parametrize(
    "scope, expected",
    [
        ("ips", ["10.0.0.5", "2001:db8::1"]),
        ("ipv4", ["10.0.0.5"]),
        ("ipv6", ["2001:db8::1"]),
        ("urls", ["https://a.example.com/x"]),
        ("domains", ["a.example.com", "b.test.org"]),
        ("subdomains", ["a.example.com", "b.test.org"]),
        ("domains, example.com", ["a.example.com"]),
        ("IPs,URLs", ["10.0.0.5", "2001:db8::1", "https://a.example.com/x"]),
    ],
)
def test_scope_type_keywords(scope, expected):
    content = "10.0.0.5 2001:db8::1 https://a.example.com/x b.test.org"
    assert filter_content(content, scope_filters=scope) == expected


def test_scope_type_keywords_combine_with_flags():
    content = "10.0.0.5 https://a.example.com/x b.test.org"
    assert filter_content(content, scope_filters=["urls"], filter_domain=True) == [
        "a.example.com", "b.test.org", "https://a.example.com/x"]


def test_split_scope():
    kinds, matcher = split_scope(["ips", "example.com", "  ", "10.0.0.0/8", "admin"])
    assert kinds == {"ipv4", "ipv6"}
    assert matcher.domains == ["example.com"]
    assert [str(n) for n in matcher.networks] == ["10.0.0.0/8"]
    assert matcher.keywords == ["admin"]


def test_empty_scope_matcher_is_falsy():
    assert not ScopeMatcher([" ", ""])
    assert split_scope(None)[0] == set()


# --- Input handling and robustness ------------------------------------------


@pytest.mark.parametrize("content", ["", None, "no indicators here"])
def test_empty_or_irrelevant_content(content):
    assert filter_content(content) == []


def test_bytes_content_is_decoded():
    assert filter_content(b"host 10.0.0.1 \xff\xfe") == ["10.0.0.1"]


def test_results_are_sorted_and_unique():
    content = "b.com a.com b.com 10.0.0.1 10.0.0.1"
    assert filter_content(content) == ["10.0.0.1", "a.com", "b.com"]


def test_pathological_input_is_fast():
    # Long dotted runs used to be quadratic for the domain regex.
    content = "a." * 200_000 + "x"
    start = time.perf_counter()
    filter_content(content)
    assert time.perf_counter() - start < 5
