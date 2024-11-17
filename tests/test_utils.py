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

from crivo.utils import normalise_text, validate_scope, log_verbose


def test_normalise_text():
    assert normalise_text("  Sample Text  ") == "sample text"


def test_validate_scope_empty():
    assert validate_scope("") == []


def test_validate_scope_valid():
    scope = "example.com, test.com"
    assert validate_scope(scope) == ["example.com", "test.com"]


def test_log_verbose(capsys):
    log_verbose("This is a test message", verbose=True)
    captured = capsys.readouterr()
    assert "This is a test message" in captured.out


def test_log_verbose_disabled(capsys):
    log_verbose("This should not appear", verbose=False)
    captured = capsys.readouterr()
    assert "This should not appear" not in captured.out
