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

import re
import os

def load_valid_tlds(file_path):
    """
    Loads a list of valid TLDs from a file and constructs a regex pattern.

    Args:
        file_path (str): Path to the file containing valid TLDs.

    Returns:
        str: A regex pattern matching valid TLDs.
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            tlds = [line.strip() for line in f if line.strip()]
        if not tlds:
            raise ValueError("The TLD list is empty.")
        # Join TLDs into a single regex group
        return '|'.join(tlds)
    except FileNotFoundError:
        raise FileNotFoundError(f"Error: The file '{file_path}' was not found.")
    except IOError as e:
        raise IOError(f"Error reading the file '{file_path}': {e}")

def filter_content(content, scope_filters=None, filter_ip=False, filter_ipv4=False, filter_ipv6=False, filter_domain=False, filter_url=False):
    """
    Filters the provided content based on specified parameters.

    Args:
        content (str): The content to be filtered.
        scope_filters (list): List of scope filters to apply.
        filter_ip (bool): Whether to filter only IPs.
        filter_ipv4 (bool): Whether to filter only IPv4 addresses.
        filter_ipv6 (bool): Whether to filter only IPv6 addresses.
        filter_domain (bool): Whether to filter only domains.
        filter_url (bool): Whether to filter only URLs.

    Returns:
        list: A list of unique filtered strings based on the criteria.
    """
    # Load the TLD regex dynamically
    tld_regex = load_valid_tlds('valid_tlds.txt')
    domain_pattern = rf'\b(?:[a-zA-Z0-9-]+\.)+(?:{tld_regex})\b'

    # Other regex patterns
    ipv4_pattern = r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b'
    ipv6_pattern = r'\b(?:[a-fA-F0-9]{1,4}:){7}[a-fA-F0-9]{1,4}\b'
    url_pattern = r'\bhttps?://[^\s<>"\'#]+\b'
    results = set()

    # Apply filters
    if filter_ip or filter_ipv4 or filter_ipv6:
        if filter_ipv4 or filter_ip:
            results.update(re.findall(ipv4_pattern, content))
        if filter_ipv6 or filter_ip:
            results.update(re.findall(ipv6_pattern, content))
    if filter_url:
        results.update(re.findall(url_pattern, content))
    if filter_domain:
        results.update(re.findall(domain_pattern, content))

    # Default behaviour: capture all if no filter is applied
    if not (filter_ip or filter_ipv4 or filter_ipv6 or filter_domain or filter_url):
        results.update(re.findall(ipv4_pattern, content))
        results.update(re.findall(ipv6_pattern, content))
        results.update(re.findall(url_pattern, content))
        results.update(re.findall(domain_pattern, content))

    # Apply scope filtering if provided
    if scope_filters:
        results = {item for item in results if any(scope in item for scope in scope_filters)}

    return sorted(results)

