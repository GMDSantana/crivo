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

import pytest
import requests
from crivo.web_scraper import scrape_webpage


def test_scrape_webpage_valid(mocker):
    mock_response = mocker.Mock()
    mock_response.text = "<html><body>Test content</body></html>"
    mock_response.raise_for_status = mocker.Mock()

    mocker.patch("requests.get", return_value=mock_response)

    content = scrape_webpage("http://example.com")
    assert content == "<html><body>Test content</body></html>"


def test_scrape_webpage_http_error(mocker):
    mock_response = mocker.Mock()
    mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError(
        "HTTP error"
    )

    mocker.patch("requests.get", return_value=mock_response)

    with pytest.raises(
        RuntimeError,
        match="Error fetching the webpage 'http://example.com': HTTP error",
    ):
        scrape_webpage("http://example.com")


def test_scrape_webpage_request_exception(mocker):
    mocker.patch(
        "requests.get",
        side_effect=requests.exceptions.RequestException("Request failed"),
    )

    with pytest.raises(
        RuntimeError,
        match="Error fetching the webpage 'http://example.com': Request failed",
    ):
        scrape_webpage("http://example.com")


def test_scrape_webpage_connection_error(mocker):
    mocker.patch(
        "requests.get", side_effect=requests.ConnectionError("Connection failed")
    )

    with pytest.raises(RuntimeError, match="Error fetching the webpage"):
        scrape_webpage("http://example.com")
