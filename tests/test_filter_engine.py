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
from crivo.filter_engine import filter_content

def test_filter_content_no_filters():
    content = "192.168.0.1 example.com https://example.com"
    result = filter_content(content)
    expected = ["192.168.0.1", "example.com", "https://example.com"]
    assert sorted(result) == sorted(expected)

def test_filter_content_ipv4():
    content = "192.168.0.1 example.com https://example.com"
    result = filter_content(content, filter_ipv4=True)
    expected = ["192.168.0.1"]
    assert sorted(result) == sorted(expected)

def test_filter_content_domain():
    content = "192.168.0.1 example.com https://example.com"
    result = filter_content(content, filter_domain=True)
    expected = ["example.com"]
    assert sorted(result) == sorted(expected)

def test_filter_content_url():
    content = "Visit https://example.com and http://test.com for details."
    result = filter_content(content, filter_url=True)
    expected = ["https://example.com", "http://test.com"]
    assert sorted(result) == sorted(expected)

def test_filter_content_with_scope():
    content = "192.168.0.1 example.com https://example.com"
    result = filter_content(content, scope_filters=["example"])
    expected = ["example.com", "https://example.com"]
    assert sorted(result) == sorted(expected)

def test_filter_content_combined_filters():
    content = "192.168.0.1 example.com https://example.com"
    result = filter_content(content, filter_ip=True, filter_url=True)
    assert sorted(result) == ["192.168.0.1", "https://example.com"]

