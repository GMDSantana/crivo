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

import requests
from urllib.parse import urljoin
import re

def scrape_webpage(url, resolve_links=False):
    """
    Fetches the content of a webpage and optionally resolves relative links.

    Args:
        url (str): The URL of the webpage to be scraped.
        resolve_links (bool): Whether to return only resolved links (default: False).

    Returns:
        str: The full content of the webpage or resolved links if `resolve_links` is True.
    """
    try:
        response = requests.get(url)
        response.raise_for_status()

        base_url = response.url  # Use the final resolved URL as the base
        content = response.text

        if resolve_links:
            # Find all href links in the content
            links = re.findall(r'href=["\'](.*?)["\']', content)

            # Convert relative links to absolute links
            resolved_links = [urljoin(base_url, link) for link in links]

            # Return resolved links as a string
            return "\n".join(resolved_links)

        # Return full content if resolve_links is False
        return content
    except requests.exceptions.RequestException as e:
        raise RuntimeError(f"Error fetching the webpage '{url}': {e}")

