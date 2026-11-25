<p align="center">
Translations <br>
<a href="README.md">🇬🇧 EN</a>
<a href="translations/es/README.md">🇪🇸 ES</a>
<a href="translations/pt-br/README.md">🇧🇷 PT-BR</a>
<a href="translations/zh-cn/README.md">🇨🇳 ZH-CN</a>
 <br><br>
</p>

# Crivo

Crivo is an open-source Python tool designed for offensive security analysts, pentesters, and bug bounty hunters. It extracts and filters URLs, IPs, domains, and subdomains from text input or web pages, with built-in web scraping capabilities. The tool supports various filtering options, scopes, and flexible output configurations.

Crivo is particularly well-suited for quick tasks and automation. Its straightforward output format, free from unnecessary clutter, makes it ideal for integrating into automated workflows. Additionally, Crivo can efficiently process and "filter" reports or outputs from other tools, such as [Amass](https://github.com/owasp-amass/amass), extracting only the information you need and presenting it in a clean, organised list.

## Features

- Extracts IPv4, IPv6 (including compressed forms such as `2001:db8::1`), URLs, domains, and subdomains from input text or web pages.
- Validates what it finds: IPs are checked octet by octet, and domains must end in a real top-level domain (bundled list, including internationalised TLDs).
- Accepts input from:
  - Single text files (any encoding; invalid bytes are tolerated).
  - Standard input, so it can sit in a pipeline (`cat report.txt | crivo`).
  - Individual web pages.
  - A list of web pages in a file.
- Supports flexible scope filtering: by result type, by domain (including subdomains), by IP or CIDR range, or by keyword.
- Outputs results directly to the console or to a specified file, maintaining the order of URLs in lists.
- Optional crawling with depth control: follows links up to a given depth while staying in scope (or on the starting site) and within a page limit.
- Robust web fetching: timeouts, automatic retries for transient errors, a size limit, redirect handling and correct character decoding.
- Provides a verbose mode for additional information during execution. Diagnostics go to standard error, so the output stays clean.

## Installation

Ensure Python 3.10 or higher is installed on your system.

```bash
# Clone the repository
git clone https://github.com/GMDSantana/crivo.git

# Navigate to the project directory
cd crivo

# Install Crivo and its dependencies into a virtual environment (.venv)
scripts/install_dependencies.sh
source .venv/bin/activate
```

Alternatively, install it with pip, which also provides the `crivo` command:

```bash
pip install .
```

## Usage

Run Crivo using the command line (`crivo`, `python -m crivo` or `python crivo.py`):

```bash
# Extract and filter from a text file
crivo -f input.txt

# Read from standard input
cat amass_output.txt | crivo --domain

# Fetch and filter from a single webpage (https:// is assumed if no scheme is given)
crivo -w https://example.com

# Also extract links from href/src/action attributes, resolving relative ones
crivo -w https://example.com -r --url

# Fetch and filter from a list of webpages
crivo -W webpage_list.txt

# Crawl two levels deep, staying on example.com and its subdomains
crivo -w https://example.com -c 2

# Fetch the in-scope URLs found in a report and extract domains from them too
crivo -f report.txt -c 1 -s example.com --domain

# Specify scope filters and output to a file
crivo -f input.txt -s example.com -o output.txt

# Only IPs inside a range, and only URLs on example.com or its subdomains
crivo -f input.txt -s ips,10.0.0.0/8
crivo -f input.txt -s urls,*.example.com

# Enable verbose output
crivo -f input.txt -v
```

### Command-Line Arguments

- `-f`, `--file`: Path to a text file containing input data to be filtered (`-` reads standard input).
- `-w`, `--webpage`: URL of a single webpage to fetch and filter.
- `-W`, `--webpage-list`: Path to a text file containing a list of webpage URLs to fetch and filter sequentially, one per line. Blank lines, lines starting with `#` and duplicates are skipped. Each URL is printed before its results.
- `-o`, `--output`: Path to the output file where filtered results will be saved. If not specified, results are printed to the console.
- `-s`, `--scope`: Comma-separated scope filters (see below). By default, all types of data are included if no scope is provided.
- `--ip`: Filter and display only IP addresses (both IPv4 and IPv6).
- `--ipv4`: Filter and display only IPv4 addresses.
- `--ipv6`: Filter and display only IPv6 addresses.
- `--domain`: Filter and display only domains and subdomains.
- `--url`: Filter and display only URLs.
- `-r`, `--resolve-links`: For webpages, also extract links from `href`, `src` and `action` attributes, resolving relative links against the page URL.
- `-t`, `--timeout`: HTTP timeout in seconds (default: 15).
- `-k`, `--insecure`: Do not verify TLS certificates (useful for test environments with self-signed certificates).
- `-c`, `--crawl DEPTH`: Crawl depth (default: `0`, no crawling). See [Crawling](#crawling).
- `--max-pages N`: Maximum number of pages to fetch per crawl (default: `100`).
- `-v`, `--verbose`: Enable verbose output to show additional details during execution (on standard error).
- `-V`, `--version`: Display the version of the Crivo programme.

`-f`, `-w` and `-W` are mutually exclusive. With none of them, Crivo reads standard input.

### Scope Filters

Each entry in `-s`/`--scope` is one of the following:

| Entry | Meaning |
| --- | --- |
| `ips`, `ipv4`, `ipv6`, `urls`, `domains`, `subdomains` | Selects result types, like the `--ip`, `--ipv4`, `--ipv6`, `--url` and `--domain` flags. `domains` and `subdomains` are equivalent. |
| `example.com`, `*.example.com`, `https://example.com/` | Keeps `example.com` and its subdomains, both as domains and as URL hosts. Look-alikes such as `notexample.com` or `example.com.evil.net` are excluded. |
| `10.0.0.5`, `10.0.0.0/8`, `2001:db8::/32` | Keeps IPs inside the address or range, including as URL hosts. |
| anything else, e.g. `admin` or `192.168.` | A case-insensitive keyword that may appear anywhere in the result. |

Type keywords and targets can be combined: `-s urls,example.com` keeps only URLs on `example.com` and its subdomains.

### Crawling

With `-c`/`--crawl`, Crivo follows links breadth-first and extracts results from every page it fetches:

- Depth `0` (default): no crawling. Crivo behaves exactly as without `-c`.
- Depth `1`: Crivo also fetches the URLs found in the initial input: the links on the page given with `-w` (or on each page of `-W`), or the URLs found in a file or standard input.
- Depth `2` and above: Crivo also follows the links on those pages, up to the given depth.

How crawling stays under control:

- **Scope is enforced at every level, including redirects.** With scope targets (for example `-s example.com` or `-s 10.0.0.0/8`), only matching URLs are fetched, and a redirect to an out-of-scope URL is not followed. Type keywords such as `urls` do not restrict crawling.
- **Without scope targets, Crivo stays on the starting site**: the starting host (ignoring a leading `www.`) and its subdomains. With a file or standard input, every URL in the input is fetched at depth 1, and their hosts define the site for deeper levels.
- **At most `--max-pages` pages** (default 100) are fetched per crawl, or per listed page with `-W`. A warning says how many in-scope URLs were left unvisited.
- Each page is fetched only once. Links to images, fonts, stylesheets, media, documents and archives are not fetched, and responses that are not text are skipped; such URLs are still reported as results when they appear in a page.
- Pages that fail during the crawl (for example with a 404) are reported in a warning and do not change the exit code; only a failure of the starting page does.
- The results of all pages are merged into one sorted list (one list per listed page with `-W`).

### Exit Codes

| Code | Meaning |
| --- | --- |
| `0` | Success (including when nothing was found). |
| `1` | An error occurred, e.g. a missing input file or a webpage that could not be fetched. With `-W`, the remaining pages are still processed. |
| `2` | Invalid command-line arguments. |
| `130` | Interrupted with Ctrl+C. |

## Running the Tests

```bash
pip install -r requirements-dev.txt
pytest --cov=crivo
```

The web scraper tests use a local HTTP server, so no internet access is needed.

## Contributing

Contributions are welcome! Before getting started, please read the [CONTRIBUTING.md](CONTRIBUTING.md) file for guidelines on how to contribute effectively. Once you're ready, fork the repository, create a feature branch, and submit a pull request with your changes.

## License

Crivo is licensed under the [MIT License](LICENSE).

## Contributors

<!-- ALL-CONTRIBUTORS-LIST:START - Do not remove or modify this section -->
<!-- prettier-ignore-start -->
<!-- markdownlint-disable -->
<table>
  <tbody>
    <tr>
      <td align="center" valign="top" width="14.28%"><a href="https://gmdsantana.com/"><img src="https://avatars.githubusercontent.com/u/6341823?v=4?s=100" width="100px;" alt="GMDSantana"/><br /><sub><b>GMDSantana</b></sub></a><br /><a href="#code-GMDSantana" title="Code">💻</a> <a href="#design-GMDSantana" title="Design">🎨</a> <a href="#doc-GMDSantana" title="Documentation">📖</a> <a href="#test-GMDSantana" title="Tests">⚠️</a></td>
    </tr>
  </tbody>
</table>

<!-- markdownlint-restore -->
<!-- prettier-ignore-end -->

<!-- ALL-CONTRIBUTORS-LIST:END -->

This project follows the [all-contributors](https://allcontributors.org) specification.
Contributions of any kind are welcome!
