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

import argparse
import logging
import os
import sys
from contextlib import contextmanager

from crivo.crawler import DEFAULT_MAX_PAGES, Crawler
from crivo.file_processor import process_file, read_stdin, read_url_list
from crivo.filter_engine import filter_content, split_scope
from crivo.utils import validate_scope
from crivo.version import __version__
from crivo.web_scraper import DEFAULT_TIMEOUT, create_session, extract_links, fetch_webpage

logger = logging.getLogger("crivo")

EXIT_OK = 0
EXIT_ERROR = 1
EXIT_INTERRUPTED = 130
EXIT_BROKEN_PIPE = 141


class CrivoError(Exception):
    """An error that is reported to the user without a traceback."""


def _positive_float(value):
    try:
        number = float(value)
    except ValueError:
        raise argparse.ArgumentTypeError(f"'{value}' is not a number") from None
    if not number > 0:
        raise argparse.ArgumentTypeError("must be greater than 0")
    return number


def _int_at_least(minimum):
    def parse(value):
        try:
            number = int(value)
        except ValueError:
            raise argparse.ArgumentTypeError(f"'{value}' is not a whole number") from None
        if number < minimum:
            raise argparse.ArgumentTypeError(f"must be {minimum} or more")
        return number
    return parse


def build_parser():
    """
    Builds the command-line parser for Crivo.

    Returns:
        argparse.ArgumentParser: The parser.
    """
    parser = argparse.ArgumentParser(
        prog="crivo",
        description=(
            "Crivo - A tool for extracting and filtering URLs, IPs, domains, and subdomains "
            "from text or web pages, with built-in web scraping capabilities."
        ),
        epilog="With no input option, Crivo reads text from standard input, e.g. 'cat report.txt | crivo'.",
    )

    source = parser.add_mutually_exclusive_group()
    source.add_argument("-f", "--file", help="Input file with text to be filtered ('-' reads standard input)", type=str)
    source.add_argument("-w", "--webpage", help="URL of a webpage to have its content filtered", type=str)
    source.add_argument("-W", "--webpage-list", help="File containing a list of webpage URLs to be filtered, one per line ('-' reads standard input)", type=str)

    parser.add_argument("-o", "--output", help="Write the output to a file instead of standard output", type=str)
    parser.add_argument(
        "-s", "--scope", type=str,
        help="Comma-separated scope filters: result types (ips, ipv4, ipv6, urls, domains, subdomains) "
             "and/or targets (example.com, *.example.com, 10.0.0.0/8, or a keyword)",
    )
    parser.add_argument("--ip", help="Filter only IPs", action="store_true")
    parser.add_argument("--ipv4", help="Filter only IPv4", action="store_true")
    parser.add_argument("--ipv6", help="Filter only IPv6", action="store_true")
    parser.add_argument("--domain", help="Filter only domains and subdomains", action="store_true")
    parser.add_argument("--url", help="Filter only URLs", action="store_true")

    web = parser.add_argument_group("web options")
    web.add_argument("-r", "--resolve-links", help="Also extract links from href/src/action attributes, resolving relative ones", action="store_true")
    web.add_argument("-t", "--timeout", help=f"HTTP timeout in seconds (default: {DEFAULT_TIMEOUT:g})", type=_positive_float, default=DEFAULT_TIMEOUT)
    web.add_argument("-k", "--insecure", help="Do not verify TLS certificates", action="store_true")

    crawl = parser.add_argument_group("crawling")
    crawl.add_argument(
        "-c", "--crawl", metavar="DEPTH", type=_int_at_least(0), default=0,
        help="Crawl depth (default: 0, no crawling). 1 also fetches the URLs found in the input; "
             "2 and above follow the links on those pages. Only in-scope URLs are fetched; "
             "without scope targets, crawling stays on the starting site",
    )
    crawl.add_argument(
        "--max-pages", metavar="N", type=_int_at_least(1), default=DEFAULT_MAX_PAGES,
        help=f"Maximum number of pages to fetch per crawl (default: {DEFAULT_MAX_PAGES})",
    )

    parser.add_argument("-v", "--verbose", help="Enable verbose output (on standard error)", action="store_true")
    parser.add_argument("-V", "--version", help="Show the programme version", action="version", version=f"Crivo {__version__}")
    return parser


def parse_arguments(argv=None):
    """
    Parses the command-line arguments for Crivo.

    Args:
        argv (list | None): Arguments to parse. Defaults to sys.argv[1:].

    Returns:
        argparse.Namespace: Parsed command-line arguments.
    """
    return build_parser().parse_args(argv)


def configure_logging(verbose):
    """Sends Crivo's log messages to standard error."""
    handler = logging.StreamHandler(sys.stderr)
    handler.setFormatter(logging.Formatter("[%(levelname)s] %(message)s"))
    logger.handlers[:] = [handler]
    logger.setLevel(logging.INFO if verbose else logging.WARNING)
    logger.propagate = False


@contextmanager
def open_output(path):
    """Yields standard output, or the file at path opened for writing."""
    if not path or path == "-":
        yield sys.stdout
        return
    try:
        handle = open(path, "w", encoding="utf-8", newline="\n")
    except OSError as exc:
        raise CrivoError(f"Cannot write to '{path}': {exc.strerror or exc}") from None
    with handle:
        yield handle


def report_error(error):
    """Prints an error message to standard error, prefixed with "Error:" once."""
    message = str(error)
    if not message.lower().startswith("error"):
        message = f"Error: {message}"
    print(message, file=sys.stderr)


def write_lines(stream, lines):
    """Writes each line followed by a newline; writes nothing for an empty list."""
    if lines:
        stream.write("\n".join(lines) + "\n")


class _Runner:
    def __init__(self, args):
        self.args = args
        self.filters = {
            "scope_filters": validate_scope(args.scope),
            "filter_ip": args.ip,
            "filter_ipv4": args.ipv4,
            "filter_ipv6": args.ipv6,
            "filter_domain": args.domain,
            "filter_url": args.url,
        }
        self._session = None
        self._crawler = None

    def filter(self, content, source):
        results = filter_content(content, **self.filters)
        logger.info("%d result(s) from %s", len(results), source)
        return results

    @property
    def session(self):
        if self._session is None:
            self._session = create_session()
            if self.args.insecure:
                import urllib3

                urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
                logger.warning("TLS certificate verification is disabled (--insecure).")
        return self._session

    def close(self):
        if self._session is not None:
            self._session.close()

    def fetch(self, url, **kwargs):
        return fetch_webpage(url, timeout=self.args.timeout, verify=not self.args.insecure, session=self.session,
                             **kwargs)

    def analyse(self, page):
        """Returns the filtered results of a fetched page."""
        content = page.text
        if self.args.resolve_links:
            links = extract_links(page.text, page.url)
            logger.info("Resolved %d link(s)", len(links))
            content = content + "\n" + "\n".join(links)
        return self.filter(content, page.url)

    @property
    def crawler(self):
        if self._crawler is None:
            _, scope = split_scope(self.filters["scope_filters"])
            self._crawler = Crawler(self.fetch, self.analyse, self.args.crawl, self.args.max_pages, scope)
        return self._crawler

    def report_crawl(self, crawl, source):
        logger.info("Crawled %d page(s) from %s; %d result(s)", crawl.fetched, source, len(crawl.results))
        if crawl.failed:
            logger.warning("%d crawled page(s) from %s could not be fetched.", crawl.failed, source)
        if crawl.not_crawled:
            logger.warning(
                "Reached --max-pages (%d) for %s; %d in-scope URL(s) were not crawled.",
                self.args.max_pages, source, crawl.not_crawled,
            )

    def fetch_and_filter(self, url):
        if self.args.crawl:
            crawl = self.crawler.crawl_url(url)
            self.report_crawl(crawl, url)
            return sorted(crawl.results)
        logger.info("Fetching %s", url)
        page = self.fetch(url)
        if page.url != url:
            logger.info("Final URL: %s", page.url)
        return self.analyse(page)

    def filter_text(self, text, source):
        results = self.filter(text, source)
        if self.args.crawl:
            crawl = self.crawler.crawl_text(text)
            self.report_crawl(crawl, source)
            results = sorted(set(results) | crawl.results)
        return results

    def run(self):
        args = self.args

        if args.webpage_list:
            urls = read_url_list(args.webpage_list)
            if not urls:
                logger.warning("No URLs found in '%s'.", args.webpage_list)
            failures = 0
            with open_output(args.output) as out:
                for url in urls:
                    write_lines(out, [url])  # print the URL first, as a header
                    try:
                        results = self.fetch_and_filter(url)
                    except RuntimeError as exc:
                        failures += 1
                        report_error(exc)
                        continue
                    write_lines(out, results)
                    out.flush()
            if failures:
                logger.warning("%d of %d webpage(s) could not be fetched.", failures, len(urls))
                return EXIT_ERROR
            return EXIT_OK

        if args.webpage:
            try:
                results = self.fetch_and_filter(args.webpage)
            except RuntimeError as exc:
                raise CrivoError(str(exc)) from None
        elif args.file:
            source = "standard input" if args.file == "-" else args.file
            logger.info("Reading %s", source)
            results = self.filter_text(process_file(args.file), source)
        elif sys.stdin is not None and not sys.stdin.isatty():
            logger.info("Reading standard input")
            results = self.filter_text(read_stdin(), "standard input")
        else:
            raise CrivoError(
                "An input file (-f), a webpage (-w), a webpage list (-W) or data on standard input is required."
            )

        with open_output(args.output) as out:
            write_lines(out, results)
        return EXIT_OK


def _silence_stdout():
    # Python flushes stdout at exit; point it at /dev/null so that does not fail too.
    try:
        devnull = os.open(os.devnull, os.O_WRONLY)
        os.dup2(devnull, sys.stdout.fileno())
    except (OSError, ValueError, AttributeError):
        pass


def main(argv=None):
    """
    Main logic for Crivo.

    Args:
        argv (list | None): Command-line arguments. Defaults to sys.argv[1:].

    Returns:
        int: The exit status: 0 on success, 1 on error, 130 if interrupted.
    """
    args = parse_arguments(argv)
    configure_logging(args.verbose)
    runner = _Runner(args)
    try:
        status = runner.run()
        sys.stdout.flush()
        return status
    except CrivoError as exc:
        report_error(exc)
        return EXIT_ERROR
    except (OSError, ValueError) as exc:
        if isinstance(exc, BrokenPipeError):
            _silence_stdout()
            return EXIT_BROKEN_PIPE
        report_error(exc)
        return EXIT_ERROR
    except KeyboardInterrupt:
        print("Interrupted.", file=sys.stderr)
        return EXIT_INTERRUPTED
    finally:
        runner.close()


if __name__ == "__main__":
    sys.exit(main())
