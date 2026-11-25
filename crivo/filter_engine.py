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

import ipaddress
import re
import string
from functools import lru_cache
from pathlib import Path
from urllib.parse import urlsplit

# The TLD list ships inside the package so Crivo works from any directory.
DEFAULT_TLD_FILE = Path(__file__).resolve().parent / "data" / "valid_tlds.txt"

# Result kinds
IPV4 = "ipv4"
IPV6 = "ipv6"
URL = "url"
DOMAIN = "domain"

# Words accepted in --scope that select result types instead of targets.
SCOPE_TYPE_KEYWORDS = {
    "ip": {IPV4, IPV6},
    "ips": {IPV4, IPV6},
    "ipv4": {IPV4},
    "ipv4s": {IPV4},
    "ipv6": {IPV6},
    "ipv6s": {IPV6},
    "url": {URL},
    "urls": {URL},
    "domain": {DOMAIN},
    "domains": {DOMAIN},
    "subdomain": {DOMAIN},
    "subdomains": {DOMAIN},
}

_HEX_DIGITS = frozenset(string.hexdigits)

# A DNS label. Underscores are accepted because DNS names such as
# "_dmarc.example.com" or "s1._domainkey.example.com" are common in recon output.
_LABEL = r"[a-z0-9_](?:[a-z0-9_-]{0,61}[a-z0-9_])?"

# Accented Latin letters. A domain must not start or end next to one, so that
# "süd.example.com" is not reported as "d.example.com". (CJK text often has no
# spaces around domains, so other scripts are allowed as neighbours.)
_LATIN_EXT = "\u00c0-\u024f"

# Candidate domain: one or more labels followed by an ASCII, punycode or
# Unicode TLD. The TLD is validated against the TLD list afterwards, which is
# much faster than a 1,500-way regex alternation. The look-behinds stop a
# match from starting in the middle of a word or of another domain, and the
# look-ahead rejects the local part of e-mail addresses.
_DOMAIN_RE = re.compile(
    rf"(?<![a-z0-9_{_LATIN_EXT}-])(?<![a-z0-9_{_LATIN_EXT}]\.)"
    rf"(?:{_LABEL}\.)+"
    r"(?:xn--[a-z0-9-]{1,59}|[a-z]{2,63}|[^\x00-\x7f\W\d_]{1,63})"
    rf"(?![a-z0-9_@{_LATIN_EXT}])",
    re.IGNORECASE,
)

# Candidate IPv4 address; validated with the ipaddress module. It must not be
# part of a longer dotted number such as a version string "1.2.3.4.5".
_IPV4_RE = re.compile(r"(?<![0-9.])(?:[0-9]{1,3}\.){3}[0-9]{1,3}(?![0-9]|\.[0-9])")

# Candidate IPv6 address in full, compressed ("2001:db8::1", "::1") or
# IPv4-mapped ("::ffff:192.0.2.1") form; validated with the ipaddress module.
# It must not start inside a longer run of colon-separated groups.
_IPV6_RE = re.compile(
    r"(?<![0-9a-z.])(?<![0-9a-f]:)"
    r"(?:[0-9a-f]{0,4}:){2,7}"
    r"(?:(?:[0-9]{1,3}\.){3}[0-9]{1,3}|[0-9a-f]{0,4})"
    r"(?![0-9a-z:])",
    re.IGNORECASE,
)

# Candidate http(s) URL. Fragments are not included, as in Crivo 1.x.
_URL_RE = re.compile(r"(?<![a-z0-9+.-])https?://[^\s<>\"'`{}|\\^#]+", re.IGNORECASE)

_URL_TRAILING_PUNCTUATION = ".,;:!?*"
_URL_CLOSERS = {")": "(", "]": "["}
_HTML_AMP_RE = re.compile(r"&(?:amp|#0*38|#x0*26);", re.IGNORECASE)

# Scope entries that are plausibly host names.
_HOSTNAME_RE = re.compile(r"^[a-z0-9_-]+(?:\.[a-z0-9_-]+)+$")


def load_valid_tlds(file_path=None):
    """
    Loads the list of valid top-level domains.

    Blank lines and lines starting with '#' are ignored. TLDs are lower-cased,
    and Unicode TLDs are also added in their punycode ("xn--") form.

    Args:
        file_path (str | Path | None): Path to the TLD list. Defaults to the
            list bundled with Crivo.

    Returns:
        frozenset: The set of valid TLDs.

    Raises:
        FileNotFoundError: If the file does not exist.
        OSError: If the file cannot be read.
        ValueError: If the file contains no TLDs.
    """
    path = Path(file_path) if file_path else DEFAULT_TLD_FILE
    try:
        with open(path, "r", encoding="utf-8") as handle:
            lines = handle.read().splitlines()
    except FileNotFoundError:
        raise FileNotFoundError(f"The TLD list '{path}' was not found.") from None
    except (OSError, UnicodeDecodeError) as exc:
        raise OSError(f"Could not read the TLD list '{path}': {exc}") from exc

    tlds = set()
    for line in lines:
        tld = line.strip().lower().lstrip(".")
        if not tld or tld.startswith("#"):
            continue
        tlds.add(tld)
        if not tld.isascii():
            try:
                tlds.add(tld.encode("idna").decode("ascii"))
            except UnicodeError:
                pass

    if not tlds:
        raise ValueError(f"The TLD list '{path}' is empty.")
    return frozenset(tlds)


@lru_cache(maxsize=1)
def _default_tlds():
    return load_valid_tlds(DEFAULT_TLD_FILE)


def _valid_domain(candidate, tlds):
    """Returns the longest prefix of candidate that ends in a valid TLD, or None."""
    labels = candidate.lower().split(".")
    for end in range(len(labels), 1, -1):
        if labels[end - 1] in tlds:
            domain = ".".join(labels[:end])
            return domain if len(domain) <= 253 else None
    return None


def extract_domains(content, tlds=None):
    """
    Extracts domains and subdomains whose TLD is in the TLD list.

    Returns:
        set: Lower-cased domain names.
    """
    tlds = _default_tlds() if tlds is None else tlds
    found = set()
    for candidate in _DOMAIN_RE.findall(content):
        domain = _valid_domain(candidate, tlds)
        if domain:
            found.add(domain)
    return found


def extract_ipv4(content):
    """
    Extracts valid IPv4 addresses (each octet 0-255).

    Returns:
        set: IPv4 addresses as written in the content.
    """
    found = set()
    for candidate in _IPV4_RE.findall(content):
        try:
            ipaddress.IPv4Address(candidate)
        except ValueError:
            continue
        found.add(candidate)
    return found


def extract_ipv6(content):
    """
    Extracts valid IPv6 addresses, including compressed forms.

    Returns:
        set: IPv6 addresses as written in the content.
    """
    found = set()
    for candidate in _IPV6_RE.findall(content):
        if not _HEX_DIGITS.intersection(candidate):
            continue  # a bare "::" is almost always noise, e.g. "a :: b"
        try:
            ipaddress.IPv6Address(candidate)
        except ValueError:
            continue
        found.add(candidate)
    return found


def _trim_url(url):
    """Removes trailing punctuation and unbalanced closing brackets."""
    while url:
        last = url[-1]
        if last in _URL_TRAILING_PUNCTUATION:
            url = url[:-1]
            continue
        opener = _URL_CLOSERS.get(last)
        if opener and url.count(last) > url.count(opener):
            url = url[:-1]
            continue
        break
    return url


def _normalise_url(url):
    """Lower-cases the scheme and host, which are case-insensitive. Returns None if invalid."""
    scheme, _, rest = url.partition("://")
    split_at = len(rest)
    for separator in "/?":
        index = rest.find(separator)
        if index != -1:
            split_at = min(split_at, index)
    netloc, path = rest[:split_at], rest[split_at:]
    userinfo, at, hostport = netloc.rpartition("@")
    normalised = f"{scheme.lower()}://{userinfo}{at}{hostport.lower()}{path}"
    try:
        if not urlsplit(normalised).hostname:
            return None
    except ValueError:  # e.g. malformed IPv6 literal or port
        return None
    return normalised


def extract_urls(content):
    """
    Extracts http and https URLs.

    Trailing punctuation is trimmed, '&amp;' is decoded and the scheme and
    host are lower-cased.

    Returns:
        set: URLs.
    """
    found = set()
    for candidate in _URL_RE.findall(content):
        url = _trim_url(_HTML_AMP_RE.sub("&", candidate))
        url = _normalise_url(url) if url else None
        if url:
            found.add(url)
    return found


def _host_of(item, kind):
    if kind == URL:
        try:
            return urlsplit(item).hostname or ""
        except ValueError:
            return ""
    return item.lower()


class ScopeMatcher:
    """
    Decides whether a result is in scope.

    Each scope entry is interpreted as follows:

    * an IP address or CIDR range ("10.0.0.0/8") matches IPs, and URLs whose
      host is an IP, inside that network;
    * a domain ("example.com", "*.example.com", "https://example.com/")
      matches that domain and all of its subdomains, for both domains and URL
      hosts, but not look-alikes such as "notexample.com" or
      "example.com.evil.net";
    * anything else ("example", "admin", "192.168.") is a case-insensitive
      keyword that matches anywhere in the result, as in Crivo 1.x.
    """

    def __init__(self, entries):
        self.networks = []
        self.domains = []
        self.keywords = []
        for raw in entries:
            self._add(raw)

    def _add(self, raw):
        entry = raw.strip().lower()
        if not entry:
            return
        if "://" in entry:
            try:
                entry = urlsplit(entry).hostname or entry
            except ValueError:
                pass
        try:
            self.networks.append(ipaddress.ip_network(entry, strict=False))
            return
        except ValueError:
            pass
        domain = entry[2:] if entry.startswith("*.") else entry
        domain = domain.strip(".")
        if _HOSTNAME_RE.match(domain) and not re.fullmatch(r"[0-9.]+", domain):
            self.domains.append(domain)
        else:
            self.keywords.append(entry)

    def __bool__(self):
        return bool(self.networks or self.domains or self.keywords)

    def matches(self, item, kind):
        lowered = item.lower()
        if any(keyword in lowered for keyword in self.keywords):
            return True

        host = _host_of(item, kind)
        if not host:
            return False

        if self.networks:
            try:
                address = ipaddress.ip_address(host)
            except ValueError:
                address = None
            if address is not None:
                return any(
                    address.version == network.version and address in network
                    for network in self.networks
                )

        return any(host == domain or host.endswith("." + domain) for domain in self.domains)


def split_scope(scope_filters):
    """
    Separates type keywords (e.g. "ips", "urls") from scope targets.

    Args:
        scope_filters (list | str | None): Scope entries, or a comma-separated string.

    Returns:
        tuple: (set of selected kinds, ScopeMatcher for the remaining targets)
    """
    if not scope_filters:
        return set(), ScopeMatcher([])
    if isinstance(scope_filters, str):
        scope_filters = scope_filters.split(",")

    kinds = set()
    targets = []
    for entry in scope_filters:
        keyword = entry.strip().lower()
        if keyword in SCOPE_TYPE_KEYWORDS:
            kinds.update(SCOPE_TYPE_KEYWORDS[keyword])
        elif keyword:
            targets.append(entry)
    return kinds, ScopeMatcher(targets)


def _prepare(content):
    if content is None:
        return ""
    if isinstance(content, bytes):
        content = content.decode("utf-8", errors="replace")
    # Un-escape JSON/JavaScript-escaped slashes, e.g. "https:\/\/example.com\/".
    return content.replace("\\/", "/")


def filter_content(content, scope_filters=None, filter_ip=False, filter_ipv4=False, filter_ipv6=False,
                   filter_domain=False, filter_url=False, *, tlds=None):
    """
    Filters the provided content based on specified parameters.

    Args:
        content (str | bytes): The content to be filtered.
        scope_filters (list | str | None): Scope entries. Type keywords such as
            "ips", "urls", "domains" select result types; other entries restrict
            results to matching targets (see ScopeMatcher).
        filter_ip (bool): Whether to filter only IPs.
        filter_ipv4 (bool): Whether to filter only IPv4 addresses.
        filter_ipv6 (bool): Whether to filter only IPv6 addresses.
        filter_domain (bool): Whether to filter only domains.
        filter_url (bool): Whether to filter only URLs.
        tlds (frozenset | None): TLDs to accept. Defaults to the bundled list.

    Returns:
        list: A sorted list of unique filtered strings based on the criteria.
    """
    content = _prepare(content)
    scope_kinds, matcher = split_scope(scope_filters)

    kinds = set(scope_kinds)
    if filter_ip or filter_ipv4:
        kinds.add(IPV4)
    if filter_ip or filter_ipv6:
        kinds.add(IPV6)
    if filter_url:
        kinds.add(URL)
    if filter_domain:
        kinds.add(DOMAIN)
    if not kinds:
        # Default behaviour: capture everything if no type is selected.
        kinds = {IPV4, IPV6, URL, DOMAIN}

    results = {}
    if IPV4 in kinds:
        results.update(dict.fromkeys(extract_ipv4(content), IPV4))
    if IPV6 in kinds:
        results.update(dict.fromkeys(extract_ipv6(content), IPV6))
    if URL in kinds:
        results.update(dict.fromkeys(extract_urls(content), URL))
    if DOMAIN in kinds:
        results.update(dict.fromkeys(extract_domains(content, tlds), DOMAIN))

    if matcher:
        results = {item: kind for item, kind in results.items() if matcher.matches(item, kind)}

    return sorted(results)
