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

import sys
import argparse
from crivo.file_processor import process_file
from crivo.web_scraper import scrape_webpage
from crivo.filter_engine import filter_content
from crivo.version import __version__

def parse_arguments():
    """
    Sets up the command-line arguments for Crivo.

    Returns:
        argparse.Namespace: Parsed command-line arguments.
    """
    parser = argparse.ArgumentParser(
        description="Crivo - A tool for extracting and filtering URLs, IPs, domains, and subdomains from text or web pages, with built-in web scraping capabilities."
    )
    
    parser.add_argument("-f", "--file", help="Input file with text to be filtered", type=str)
    parser.add_argument("-w", "--webpage", help="URL of a webpage to have its content filtered", type=str)
    parser.add_argument("-W", "--webpage-list", help="File containing a list of webpage URLs to be filtered", type=str)
    parser.add_argument("-o", "--output", help="Write the output to a file", type=str)
    parser.add_argument("-s", "--scope", help="Comma-separated sequence of scope filters (ips, urls, domains, subdomains)", type=str)
    parser.add_argument("--ip", help="Filter only IPs", action="store_true")
    parser.add_argument("--ipv4", help="Filter only IPv4", action="store_true")
    parser.add_argument("--ipv6", help="Filter only IPv6", action="store_true")
    parser.add_argument("--domain", help="Filter only domains and subdomains", action="store_true")
    parser.add_argument("--url", help="Filter only URLs", action="store_true")
    parser.add_argument("-v", "--verbose", help="Enable verbose output", action="store_true")
    parser.add_argument("-V", "--version", help="Show the programme version", action="version", version=f"Crivo {__version__}")

    return parser.parse_args()

def main():
    """
    Main logic for Crivo.
    """
    args = parse_arguments()

    if args.file:
        content = process_file(args.file)
        filtered_output = filter_content(
            content, args.scope.split(",") if args.scope else [], args.ip, args.ipv4, args.ipv6, args.domain, args.url
        )
        print("\n".join(filtered_output))

    elif args.webpage:
        print(args.webpage)
        content = scrape_webpage(args.webpage)
        filtered_output = filter_content(
            content, args.scope.split(",") if args.scope else [], args.ip, args.ipv4, args.ipv6, args.domain, args.url
        )
        print("\n".join(filtered_output))

    elif args.webpage_list:
        try:
            with open(args.webpage_list, "r", encoding="utf-8") as file:
                urls = [line.strip() for line in file if line.strip()]

            all_results = []
            for url in urls:
                print(url)  # Print the URL first
                try:
                    content = scrape_webpage(url)
                    filtered_output = filter_content(
                        content, args.scope.split(",") if args.scope else [], args.ip, args.ipv4, args.ipv6, args.domain, args.url
                    )
                    print("\n".join(filtered_output))  # Print results directly after the URL
                except Exception as e:
                    print(f"Error fetching content from {url}: {e}", file=sys.stderr)

        except FileNotFoundError:
            print(f"Error: The file '{args.webpage_list}' was not found.", file=sys.stderr)
            sys.exit(1)
    else:
        print("Error: An input file (-f), a webpage (-w), or a webpage list (-W) is required.", file=sys.stderr)
        sys.exit(1)
        
if __name__ == "__main__":
    main()
