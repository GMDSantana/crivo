# Changelog

## 2.0.0

Crivo 2 is a robustness release based on Crivo 1.0.0 (GMDSantana/crivo@08d840c).

### Fixed

- Crivo crashed unless it was run from the repository root, because `valid_tlds.txt` was opened relative to the current directory. The TLD list now ships inside the package (`crivo/data/`), so the installed `crivo` command works from anywhere.
- `-o/--output` was accepted but never wrote anything. Output is now written to the file, and an existing file is not truncated if reading the input fails.
- `-v/--verbose` did nothing. Verbose messages are now written to standard error.
- Web requests had no timeout and could hang forever. Requests now use a timeout (default 15 s, `-t`), retry transient failures (connection errors, 429 and 5xx) and limit the body to 10 MiB.
- Compressed IPv6 addresses (`2001:db8::1`, `::1`, `fe80::1`, `::ffff:192.0.2.1`) were not found; only the full eight-group form was.
- Invalid IPv4 addresses such as `999.999.999.999` were reported, and version strings such as `1.2.3.4.5` produced `1.2.3.4`.
- Upper-case domains (`EXAMPLE.COM`) and URLs (`HTTPS://…`) were not found. Domains are now reported in lower case and de-duplicated.
- URLs lost a trailing `/` and closing parentheses, so `https://en.wikipedia.org/wiki/Foo_(bar)` became `…Foo_(bar`. HTML-escaped `&amp;` in URLs is now decoded, and JSON-escaped URLs (`https:\/\/…`) are found.
- Scope entries were matched as raw substrings, so `-s example.com` also matched `notexample.com` and `example.com.evil.net`, and an entry after `, ` (with a space) never matched anything.
- Missing files, directories, invalid URLs and network errors produced Python tracebacks. They now produce a one-line error message and exit code 1.
- Files that were not valid UTF-8 caused a `UnicodeDecodeError`. Invalid bytes are now replaced.
- Web pages without a declared charset were decoded as Latin-1, garbling UTF-8 text. The `<meta charset>` tag and UTF-8 are now tried first.
- `-w` printed the requested URL as if it were a result.
- When nothing was found, an empty line was printed.
- Giving `-f` together with `-w` silently ignored `-w`; the input options are now mutually exclusive.
- `scripts/install_dependencies.sh` upgraded every system package, failed unless run from `scripts/`, and installed into the system Python (which fails on recent Debian/Ubuntu). It now installs into a `.venv` and works from any directory.
- `setup.py` read `requirements.txt` relative to the current directory and did not package the TLD list.
- The CI matrix tested Python 3.7–3.9, which cannot install the pinned dependencies (they require Python 3.10+).
- `requirements.txt` allowed urllib3 1.26.0, which cannot be imported on Python 3.12 or newer. urllib3 2.8.0 or newer is now required, which also brings fixes for the streaming decompression vulnerabilities CVE-2025-66418, CVE-2025-66471, CVE-2026-21441, CVE-2026-44432 and CVE-2026-97688 (Crivo streams responses from untrusted servers).
- Building the package raised setuptools deprecation warnings (license classifier, undeclared data package) and fell back to an old setuptools; `pyproject.toml` now declares `setuptools>=77`.
- The translated READMEs described Crivo 1.x (Python 3.7) and linked to a `master` branch and to a wrong LICENSE path.
- The language links in README, CONTRIBUTING and CODE_OF_CONDUCT (all languages) pointed to a non-existent `master` branch; they are now relative links.

### Added

- Crawling with depth control (issue #12): `-c/--crawl DEPTH` and `--max-pages N` (default 100). Scope is enforced at every level, including redirects, which are checked before they are followed; without scope targets, crawling stays on the starting site. Pages are fetched once, links to images, media, documents and archives are not fetched, and non-text responses are skipped. Without `-c`, behaviour is unchanged.
- Reading from standard input (`cat file | crivo`, or `-f -`).
- `-r/--resolve-links` to also extract links from `href`, `src` and `action` attributes, resolving relative links.
- `-t/--timeout` and `-k/--insecure` for web requests.
- Scope entries can be CIDR ranges (`10.0.0.0/8`), wildcards (`*.example.com`) or result types (`ips`, `urls`, `domains`, …), as the help text already described.
- DNS names with underscores, such as `_dmarc.example.com`, are extracted in full.
- `python -m crivo`.
- Meaningful exit codes (see the README).
- A much larger test suite (268 tests), including end-to-end tests against a local HTTP server.
- `pyproject.toml`, and a CI job that tests the oldest dependency versions allowed by the requirements files.
- Dependabot now also keeps the GitHub Actions used by the workflows up to date.

### Changed

- Python 3.10 or newer is required (as already required by the pinned dependencies).
- Domain matching validates the TLD with a set lookup instead of a 1,500-way regular expression, which is faster and avoids quadratic behaviour on long dotted input.
- `--scope` keywords without a dot (e.g. `example`, `admin`) still match anywhere, as before. Entries that look like a domain now match that domain and its subdomains only.
- `load_valid_tlds()` now returns a `frozenset` of TLDs instead of a regular-expression string.
