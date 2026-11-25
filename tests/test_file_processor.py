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

import io
import os
import sys

import pytest

from crivo.file_processor import process_file, read_stdin, read_url_list


def test_process_file_valid(tmp_path):
    path = tmp_path / "temp_test_file.txt"
    path.write_text("Sample content for testing.", encoding="utf-8")
    assert process_file(str(path)) == "Sample content for testing."


def test_process_file_not_found():
    with pytest.raises(FileNotFoundError, match="was not found"):
        process_file("non_existent_file.txt")


def test_process_file_io_error(mocker):
    mocker.patch("builtins.open", side_effect=IOError("Mocked IO error"))
    with pytest.raises(IOError, match="Mocked IO error"):
        process_file("mocked_file.txt")


def test_process_file_invalid_utf8_is_replaced(tmp_path):
    # Regression: 1.x raised UnicodeDecodeError on non-UTF-8 input.
    path = tmp_path / "binary.txt"
    path.write_bytes(b"x\xff\xfe example.com \x00")
    content = process_file(str(path))
    assert "example.com" in content
    assert "�" in content


def test_process_file_strips_bom(tmp_path):
    path = tmp_path / "bom.txt"
    path.write_bytes(b"\xef\xbb\xbfexample.com")
    assert process_file(str(path)) == "example.com"


def test_process_file_directory(tmp_path):
    with pytest.raises(IsADirectoryError, match="is a directory"):
        process_file(str(tmp_path))


@pytest.mark.skipif(os.name != "posix" or os.geteuid() == 0, reason="needs a non-root POSIX user")
def test_process_file_permission_denied(tmp_path):
    path = tmp_path / "secret.txt"
    path.write_text("x", encoding="utf-8")
    path.chmod(0)
    try:
        with pytest.raises(PermissionError, match="Permission denied"):
            process_file(str(path))
    finally:
        path.chmod(0o600)


def test_process_file_dash_reads_stdin(monkeypatch):
    monkeypatch.setattr(sys, "stdin", io.TextIOWrapper(io.BytesIO(b"10.0.0.1 \xff"), encoding="utf-8"))
    assert process_file("-").startswith("10.0.0.1 ")


def test_read_stdin_without_buffer(monkeypatch):
    monkeypatch.setattr(sys, "stdin", io.StringIO("plain text"))
    assert read_stdin() == "plain text"


def test_read_stdin_when_missing(monkeypatch):
    monkeypatch.setattr(sys, "stdin", None)
    assert read_stdin() == ""


def test_read_url_list(tmp_path):
    path = tmp_path / "urls.txt"
    path.write_text(
        "# targets\n\nhttps://a.example.com\n  https://b.example.com  \nhttps://a.example.com\n#https://c.example.com\n",
        encoding="utf-8",
    )
    assert read_url_list(str(path)) == ["https://a.example.com", "https://b.example.com"]
