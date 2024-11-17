# Crivo

Crivo is an open-source Python programme designed for offensive security analysts, pentesters, and bug bounty hunters. It extracts and filters URLs, IPs, domains, and subdomains from text input or web pages, with built-in web scraping capabilities. The programme supports various filtering options, scopes, and flexible output configurations.

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
Contributions are welcome! Please fork the repository, create a feature branch, and submit a pull request with your changes.

## License
Crivo is licensed under the [MIT License](LICENSE).

