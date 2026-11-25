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
import subprocess
import sys
from pathlib import Path

import pytest

from crivo import main as crivo_main
from crivo.main import EXIT_BROKEN_PIPE, EXIT_ERROR, EXIT_INTERRUPTED, EXIT_OK, main, parse_arguments
from crivo.version import __version__
from crivo.web_scraper import FetchResult

REPO_ROOT = Path(__file__).resolve().parent.parent
SAMPLE = "Hosts: 10.0.0.1, 2001:db8::1, a.example.com and https://b.example.com/login\nnoise: 999.1.1.1 notatld.zzzz\n"


@pytest.fixture
def sample_file(tmp_path):
    path = tmp_path / "input.txt"
    path.write_text(SAMPLE, encoding="utf-8")
    return path


class _TTY(io.StringIO):
    def isatty(self):
        return True


# --- Argument parsing --------------------------------------------------------


def test_parse_arguments_defaults():
    args = parse_arguments(["-f", "x.txt"])
    assert args.file == "x.txt"
    assert args.timeout > 0
    assert not (args.insecure or args.resolve_links or args.verbose)


def test_version_flag(capsys):
    with pytest.raises(SystemExit) as excinfo:
        main(["-V"])
    assert excinfo.value.code == 0
    assert capsys.readouterr().out.strip() == f"Crivo {__version__}"


def test_input_options_are_mutually_exclusive(capsys):
    # Regression: 1.x silently ignored -w when -f was also given.
    with pytest.raises(SystemExit) as excinfo:
        main(["-f", "a.txt", "-w", "https://example.com"])
    assert excinfo.value.code == 2
    assert "not allowed with" in capsys.readouterr().err


@pytest.mark.parametrize("value", ["0", "-1", "abc"])
def test_invalid_timeout(value, capsys):
    with pytest.raises(SystemExit) as excinfo:
        main(["-w", "example.com", "-t", value])
    assert excinfo.value.code == 2
    assert "--timeout" in capsys.readouterr().err


# --- File input ---------------------------------------------------------------


def test_file_input(sample_file, capsys):
    assert main(["-f", str(sample_file)]) == EXIT_OK
    out = capsys.readouterr().out.splitlines()
    assert out == ["10.0.0.1", "2001:db8::1", "a.example.com", "b.example.com", "https://b.example.com/login"]


@pytest.mark.parametrize(
    "flags, expected",
    [
        (["--ip"], ["10.0.0.1", "2001:db8::1"]),
        (["--ipv4"], ["10.0.0.1"]),
        (["--ipv6"], ["2001:db8::1"]),
        (["--url"], ["https://b.example.com/login"]),
        (["--domain"], ["a.example.com", "b.example.com"]),
        (["-s", "urls"], ["https://b.example.com/login"]),
        (["-s", "a.example.com, 10.0.0.0/8"], ["10.0.0.1", "a.example.com"]),
        (["--domain", "-s", "B.EXAMPLE.COM"], ["b.example.com"]),
    ],
)
def test_file_input_with_filters(sample_file, capsys, flags, expected):
    assert main(["-f", str(sample_file), *flags]) == EXIT_OK
    assert capsys.readouterr().out.splitlines() == expected


def test_no_results_prints_nothing(tmp_path, capsys):
    # Regression: 1.x printed an empty line when nothing was found.
    path = tmp_path / "empty.txt"
    path.write_text("nothing to see here", encoding="utf-8")
    assert main(["-f", str(path)]) == EXIT_OK
    assert capsys.readouterr().out == ""


def test_missing_file(capsys):
    # Regression: 1.x crashed with a traceback.
    assert main(["-f", "/definitely/not/here.txt"]) == EXIT_ERROR
    captured = capsys.readouterr()
    assert captured.out == ""
    assert captured.err.strip() == "Error: The file '/definitely/not/here.txt' was not found."


def test_directory_as_file(tmp_path, capsys):
    assert main(["-f", str(tmp_path)]) == EXIT_ERROR
    assert "is a directory" in capsys.readouterr().err


def test_runs_from_another_directory(sample_file, tmp_path, monkeypatch, capsys):
    other = tmp_path / "elsewhere"
    other.mkdir()
    monkeypatch.chdir(other)
    assert main(["-f", str(sample_file), "--domain"]) == EXIT_OK
    assert capsys.readouterr().out.splitlines() == ["a.example.com", "b.example.com"]


# --- Output file --------------------------------------------------------------


def test_output_file(sample_file, tmp_path, capsys):
    # Regression: 1.x accepted -o but never wrote the file.
    output = tmp_path / "out.txt"
    assert main(["-f", str(sample_file), "--ipv4", "-o", str(output)]) == EXIT_OK
    assert capsys.readouterr().out == ""
    assert output.read_text(encoding="utf-8") == "10.0.0.1\n"


def test_output_dash_means_stdout(sample_file, capsys):
    assert main(["-f", str(sample_file), "--ipv4", "-o", "-"]) == EXIT_OK
    assert capsys.readouterr().out == "10.0.0.1\n"


def test_output_unwritable(sample_file, tmp_path, capsys):
    output = tmp_path / "missing-dir" / "out.txt"
    assert main(["-f", str(sample_file), "-o", str(output)]) == EXIT_ERROR
    assert "Cannot write to" in capsys.readouterr().err


def test_output_not_truncated_when_input_is_missing(tmp_path, capsys):
    output = tmp_path / "out.txt"
    output.write_text("previous results\n", encoding="utf-8")
    assert main(["-f", str(tmp_path / "missing.txt"), "-o", str(output)]) == EXIT_ERROR
    assert output.read_text(encoding="utf-8") == "previous results\n"


def test_output_can_overwrite_input(sample_file, capsys):
    assert main(["-f", str(sample_file), "--ipv4", "-o", str(sample_file)]) == EXIT_OK
    assert sample_file.read_text(encoding="utf-8") == "10.0.0.1\n"


# --- Standard input -----------------------------------------------------------


def test_reads_piped_stdin(monkeypatch, capsys):
    monkeypatch.setattr(sys, "stdin", io.TextIOWrapper(io.BytesIO(SAMPLE.encode()), encoding="utf-8"))
    assert main(["--ipv4"]) == EXIT_OK
    assert capsys.readouterr().out == "10.0.0.1\n"


def test_file_dash_reads_stdin(monkeypatch, capsys):
    monkeypatch.setattr(sys, "stdin", io.StringIO(SAMPLE))
    assert main(["-f", "-", "--ipv6"]) == EXIT_OK
    assert capsys.readouterr().out == "2001:db8::1\n"


def test_no_input_on_a_terminal(monkeypatch, capsys):
    monkeypatch.setattr(sys, "stdin", _TTY())
    assert main([]) == EXIT_ERROR
    assert "is required" in capsys.readouterr().err


def test_no_input_without_stdin(monkeypatch, capsys):
    monkeypatch.setattr(sys, "stdin", None)
    assert main([]) == EXIT_ERROR
    assert "is required" in capsys.readouterr().err


# --- Verbose ------------------------------------------------------------------


def test_verbose_goes_to_stderr(sample_file, capsys):
    assert main(["-f", str(sample_file), "--ipv4", "-v"]) == EXIT_OK
    captured = capsys.readouterr()
    assert captured.out == "10.0.0.1\n"
    assert "[INFO] Reading" in captured.err
    assert "1 result(s)" in captured.err


def test_not_verbose_is_quiet(sample_file, capsys):
    main(["-f", str(sample_file)])
    assert capsys.readouterr().err == ""


# --- Webpages (local HTTP server) --------------------------------------------


def test_webpage(http_server, capsys):
    assert main(["-w", f"{http_server}/page"]) == EXIT_OK
    out = capsys.readouterr().out.splitlines()
    # Regression: 1.x printed the requested URL as if it were a result.
    assert f"{http_server}/page" not in out
    for expected in [
        "10.20.30.40",
        "2001:db8::42",
        "api.example.com",
        "docs.example.com",
        "example.com",
        "external.example.org",
        "https://docs.example.com/guide",
        "https://external.example.org/x?a=1&b=2",
    ]:
        assert expected in out
    assert f"{http_server}/about" not in out


def test_webpage_resolve_links(http_server, capsys):
    assert main(["-w", f"{http_server}/page", "-r", "--url"]) == EXIT_OK
    out = capsys.readouterr().out.splitlines()
    assert f"{http_server}/about" in out
    assert f"{http_server}/login" in out
    assert f"{http_server}/img/logo.png" in out
    assert "https://external.example.org/x?a=1&b=2" in out


def test_webpage_json_escaped_urls(http_server, capsys):
    assert main(["-w", f"{http_server}/json", "--url"]) == EXIT_OK
    assert capsys.readouterr().out == "https://api.example.com/v2/items\n"


def test_webpage_error(http_server, capsys):
    assert main(["-w", f"{http_server}/notfound"]) == EXIT_ERROR
    captured = capsys.readouterr()
    assert captured.out == ""
    assert captured.err.startswith("Error fetching the webpage")
    assert "Error: Error" not in captured.err


def test_webpage_without_scheme_is_accepted(mocker, capsys):
    fetch = mocker.patch.object(crivo_main, "fetch_webpage", return_value=FetchResult("https://example.com", "1.2.3.4"))
    assert main(["-w", "example.com"]) == EXIT_OK
    assert fetch.call_args.args[0] == "example.com"
    assert capsys.readouterr().out == "1.2.3.4\n"


def test_webpage_options_are_passed(mocker, capsys):
    fetch = mocker.patch.object(crivo_main, "fetch_webpage", return_value=FetchResult("https://example.com", ""))
    assert main(["-w", "https://example.com", "-k", "-t", "2.5"]) == EXIT_OK
    assert fetch.call_args.kwargs["verify"] is False
    assert fetch.call_args.kwargs["timeout"] == 2.5
    assert "verification is disabled" in capsys.readouterr().err


def test_webpage_list(http_server, tmp_path, capsys):
    urls = tmp_path / "urls.txt"
    urls.write_text(
        f"# my targets\n{http_server}/latin1\n\n{http_server}/notfound\n{http_server}/json\n{http_server}/latin1\n",
        encoding="utf-8",
    )
    assert main(["-W", str(urls)]) == EXIT_ERROR  # one URL failed
    captured = capsys.readouterr()
    assert captured.out.splitlines() == [
        f"{http_server}/latin1",
        "192.0.2.7",
        f"{http_server}/notfound",
        f"{http_server}/json",
        "api.example.com",
        "https://api.example.com/v2/items",
    ]
    assert "404" in captured.err
    assert "1 of 3 webpage(s) could not be fetched" in captured.err


def test_webpage_list_all_successful_to_file(http_server, tmp_path, capsys):
    urls = tmp_path / "urls.txt"
    urls.write_text(f"{http_server}/json\n", encoding="utf-8")
    output = tmp_path / "out.txt"
    assert main(["-W", str(urls), "-o", str(output)]) == EXIT_OK
    assert output.read_text(encoding="utf-8") == f"{http_server}/json\napi.example.com\nhttps://api.example.com/v2/items\n"
    assert capsys.readouterr().out == ""


def test_webpage_list_missing(capsys):
    assert main(["-W", "/no/such/list.txt"]) == EXIT_ERROR
    assert "was not found" in capsys.readouterr().err


def test_webpage_list_empty(tmp_path, capsys):
    urls = tmp_path / "urls.txt"
    urls.write_text("# nothing yet\n\n", encoding="utf-8")
    assert main(["-W", str(urls)]) == EXIT_OK
    captured = capsys.readouterr()
    assert captured.out == ""
    assert "No URLs found" in captured.err


# --- Interruptions and pipes --------------------------------------------------


def test_keyboard_interrupt(mocker, sample_file, capsys):
    mocker.patch.object(crivo_main, "process_file", side_effect=KeyboardInterrupt)
    assert main(["-f", str(sample_file)]) == EXIT_INTERRUPTED
    assert "Interrupted" in capsys.readouterr().err


def test_broken_pipe(monkeypatch, sample_file):
    class ClosedPipe(io.StringIO):
        def write(self, text):
            raise BrokenPipeError

        def fileno(self):
            raise io.UnsupportedOperation("no fileno")

    monkeypatch.setattr(sys, "stdout", ClosedPipe())
    assert main(["-f", str(sample_file)]) == EXIT_BROKEN_PIPE


# --- Real command-line invocations -------------------------------------------


def _run(args, cwd, stdin=None):
    env = dict(os.environ, PYTHONPATH=str(REPO_ROOT), PYTHONDONTWRITEBYTECODE="1")
    return subprocess.run(
        [sys.executable, *args], cwd=cwd, env=env, input=stdin, capture_output=True, text=True, timeout=60,
        stdin=None if stdin is not None else subprocess.DEVNULL,
    )


@pytest.mark.parametrize("entry", [["-m", "crivo"], [str(REPO_ROOT / "crivo.py")]])
def test_cli_entry_points(entry, sample_file, tmp_path):
    result = _run([*entry, "-f", str(sample_file), "--ipv4"], cwd=tmp_path)
    assert result.returncode == 0, result.stderr
    assert result.stdout == "10.0.0.1\n"


def test_cli_pipe(tmp_path):
    result = _run(["-m", "crivo", "--domain"], cwd=tmp_path, stdin=SAMPLE)
    assert result.returncode == 0, result.stderr
    assert result.stdout.splitlines() == ["a.example.com", "b.example.com"]


def test_cli_error_has_no_traceback(tmp_path):
    result = _run(["-m", "crivo", "-f", "missing.txt"], cwd=tmp_path)
    assert result.returncode == 1
    assert "Traceback" not in result.stderr
    assert result.stderr.strip() == "Error: The file 'missing.txt' was not found."


# --- Crawling (issue #12) -----------------------------------------------------

SITE_MARKERS = {
    "root": "127.1.0.1", "a": "127.1.0.2", "a2": "127.1.0.3", "a3": "127.1.0.4",
    "b": "127.1.0.5", "c": "127.1.0.6", "offsite": "127.1.0.99", "secret": "127.1.0.98", "binary": "127.1.0.97",
}


def _markers(*names):
    return sorted(SITE_MARKERS[name] for name in names)


def test_crawl_option_validation(capsys):
    for args in (["-c", "-1"], ["-c", "x"], ["--max-pages", "0"]):
        with pytest.raises(SystemExit) as excinfo:
            main(["-w", "example.com", *args])
        assert excinfo.value.code == 2
    assert "must be" in capsys.readouterr().err


def test_no_crawl_is_unchanged(http_server, capsys):
    assert main(["-w", f"{http_server}/site/", "--ipv4"]) == EXIT_OK
    assert capsys.readouterr().out.splitlines() == _markers("root")
    assert main(["-w", f"{http_server}/site/", "--ipv4", "-c", "0"]) == EXIT_OK
    assert capsys.readouterr().out.splitlines() == _markers("root")


@pytest.mark.parametrize(
    "depth, pages",
    [
        ("1", ["root", "a", "b", "c"]),
        ("2", ["root", "a", "b", "c", "a2"]),
        ("3", ["root", "a", "b", "c", "a2", "a3"]),
    ],
)
def test_crawl_depth_stays_on_the_site(http_server, http_hits, capsys, depth, pages):
    secret_hits = http_hits["/site/secret"]
    offsite_hits = http_hits["/site/offsite"]
    assert main(["-w", f"{http_server}/site/", "--ipv4", "-c", depth]) == EXIT_OK
    captured = capsys.readouterr()
    # Not offsite (another host), not the redirect target on another host, not binary.
    assert captured.out.splitlines() == _markers(*pages)
    assert http_hits["/site/secret"] == secret_hits
    assert http_hits["/site/offsite"] == offsite_hits
    assert "1 crawled page(s)" in captured.err  # /site/missing returned 404


def test_crawl_does_not_fetch_skipped_extensions(http_server, http_hits, capsys):
    before = http_hits["/site/image.png"]
    assert main(["-w", f"{http_server}/site/", "-c", "1"]) == EXIT_OK
    assert http_hits["/site/image.png"] == before


def test_crawl_scope_targets_widen_and_restrict(http_server, capsys):
    # "localhost" is a keyword target, 127.0.0.0/8 matches the local server and the markers.
    assert main(["-w", f"{http_server}/site/", "-s", "ipv4,localhost,127.0.0.0/8", "-c", "1"]) == EXIT_OK
    assert capsys.readouterr().out.splitlines() == _markers("root", "a", "b", "c", "offsite", "secret")

    # Only URLs containing "/site/a" are followed; markers stay in scope via 127.1.0.0/16.
    assert main(["-w", f"{http_server}/site/", "-s", "ipv4,/site/a,127.1.0.0/16", "-c", "3"]) == EXIT_OK
    assert capsys.readouterr().out.splitlines() == _markers("root", "a", "a2", "a3")


def test_crawl_max_pages(http_server, capsys):
    assert main(["-w", f"{http_server}/site/", "--ipv4", "-c", "3", "--max-pages", "3"]) == EXIT_OK
    captured = capsys.readouterr()
    assert captured.out.splitlines() == _markers("root", "a", "b")
    assert "Reached --max-pages (3)" in captured.err


def test_crawl_with_resolve_links(http_server, capsys):
    assert main(["-w", f"{http_server}/site/", "--url", "-r", "-c", "1"]) == EXIT_OK
    out = capsys.readouterr().out.splitlines()
    assert f"{http_server}/site/a2" in out  # a link found on a crawled page


def test_crawl_verbose(http_server, capsys):
    assert main(["-w", f"{http_server}/site/", "--ipv4", "-c", "1", "-v"]) == EXIT_OK
    err = capsys.readouterr().err
    assert "Crawling (depth 1)" in err
    assert "out of scope" in err
    assert "Skipped" in err and "application/octet-stream" in err


def test_crawl_start_page_error(http_server, capsys):
    assert main(["-w", f"{http_server}/notfound", "-c", "2"]) == EXIT_ERROR
    assert capsys.readouterr().err.startswith("Error fetching the webpage")


def test_crawl_webpage_list(http_server, tmp_path, capsys):
    urls = tmp_path / "urls.txt"
    urls.write_text(f"{http_server}/site/a\n{http_server}/site/b\n{http_server}/notfound\n", encoding="utf-8")
    assert main(["-W", str(urls), "--ipv4", "-c", "1"]) == EXIT_ERROR
    captured = capsys.readouterr()
    assert captured.out.splitlines() == [
        f"{http_server}/site/a", *_markers("a", "a2", "root"),
        f"{http_server}/site/b", *_markers("b", "a"),
        f"{http_server}/notfound",
    ]
    assert "1 of 3 webpage(s) could not be fetched" in captured.err


def test_crawl_from_file(http_server, tmp_path, capsys):
    other = http_server.replace("127.0.0.1", "localhost")
    path = tmp_path / "input.txt"
    path.write_text(f"marker 127.1.0.50\n{http_server}/site/a\n{other}/site/offsite\n", encoding="utf-8")
    in_text = ["127.0.0.1", "127.1.0.50"]  # IPs in the file itself
    # Depth 1: the URLs in the file are fetched, whatever their host (no scope given).
    assert main(["-f", str(path), "--ipv4", "-c", "1"]) == EXIT_OK
    assert capsys.readouterr().out.splitlines() == sorted([*in_text, *_markers("a", "offsite")])
    # Depth 2: links on those pages, staying on their sites.
    assert main(["-f", str(path), "--ipv4", "-c", "2"]) == EXIT_OK
    assert capsys.readouterr().out.splitlines() == sorted([*in_text, *_markers("a", "offsite", "a2", "root")])


def test_crawl_from_stdin(http_server, monkeypatch, capsys):
    monkeypatch.setattr(sys, "stdin", io.StringIO(f"start at {http_server}/site/b"))
    assert main(["--ipv4", "-c", "1"]) == EXIT_OK
    assert capsys.readouterr().out.splitlines() == ["127.0.0.1", *_markers("b")]
    monkeypatch.setattr(sys, "stdin", io.StringIO(f"start at {http_server}/site/b"))
    assert main(["--ipv4", "-c", "2"]) == EXIT_OK
    assert capsys.readouterr().out.splitlines() == ["127.0.0.1", *_markers("a", "b")]
