<p align="center">
Translations <br>
<a href=https://github.com/GMDSantana/crivo/tree/master/README.md>🇬🇧 EN</a>
<a href=https://github.com/GMDSantana/crivo/tree/master/translations/es/README.md>🇪🇸 ES</a>
<a href=https://github.com/GMDSantana/crivo/tree/master/translations/pt-br/README.md>🇧🇷 PT-BR</a>
<a href=https://github.com/GMDSantana/crivo/tree/master/translations/zh-cn/README.md>🇨🇳 ZH-CN</a>
 <br><br>
</p>

# Crivo

Crivo is an open-source Python tool designed for offensive security analysts, pentesters, and bug bounty hunters. It extracts and filters URLs, IPs, domains, and subdomains from text input or web pages, with built-in web scraping capabilities. The tool supports various filtering options, scopes, and flexible output configurations.

Crivo is particularly well-suited for quick tasks and automation. Its straightforward output format, free from unnecessary clutter, makes it ideal for integrating into automated workflows. Additionally, Crivo can efficiently process and "filter" reports or outputs from other tools, such as [Amass](https://github.com/owasp-amass/amass), extracting only the information you need and presenting it in a clean, organised list.

## Features

- Extracts IPv4, IPv6, URLs, domains, and subdomains from input text or web pages.
- Accepts input from:
  - Single text files.
  - A list of web pages in a file.
  - Individual web pages.
- Supports flexible scope filtering with detailed control over IPs, domains, and URLs.
- Outputs results directly to the console or to a specified file, maintaining the order of URLs in lists.
- Provides a verbose mode for additional information during execution.

## Installation

Ensure Python 3.7 or higher is installed on your system.

```bash
# Clone the repository
git clone https://github.com/GMDSantana/crivo.git

# Navigate to the project directory
cd crivo

# Install required dependencies
pip install -r requirements.txt
```

## Usage

Run Crivo using the command line:

```bash
# Extract and filter from a text file
python crivo_cli.py -f input.txt

# Fetch and filter from a single webpage
python crivo_cli.py -w https://example.com

# Fetch and filter from a list of webpages
python crivo_cli.py -W webpage_list.txt

# Specify scope filters and output to a file
python crivo_cli.py -f input.txt -s example.com -o output.txt

# Enable verbose mode for detailed output
python crivo_cli.py -f input.txt -v
```

### Command-Line Arguments

- `-f`, `--file`: Path to a text file containing input data to be filtered.
- `-w`, `--webpage`: URL of a single webpage to fetch and filter.
- `-W`, `--webpage-list`: Path to a text file containing a list of webpage URLs to fetch and filter sequentially.
- `-o`, `--output`: Path to the output file where filtered results will be saved. If not specified, results are printed to the console.
- `-s`, `--scope`: Comma-separated sequence of filters to narrow the output (e.g., `ips, urls, domains`). By default, all types of data are included if no scope is provided.
- `--ip`: Filter and display only IP addresses (both IPv4 and IPv6).
- `--ipv4`: Filter and display only IPv4 addresses.
- `--ipv6`: Filter and display only IPv6 addresses.
- `--domain`: Filter and display only domains and subdomains.
- `--url`: Filter and display only URLs.
- `-v`, `--verbose`: Enable verbose output to show additional details during execution.
- `-V`, `--version`: Display the version of the Crivo programme.

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
