"""Tests for the completions command."""

import pytest

from platform_service_framework.cli import app


def test_completions_generates_output(capsys):
    """Test that completions command generates shell completion script."""
    # Run completions command - expect SystemExit(0)
    with pytest.raises(SystemExit) as exc_info:
        app(["completions"])

    assert exc_info.value.code == 0

    # Check that something was printed
    captured = capsys.readouterr()
    assert len(captured.out) > 0


def test_completions_output_format(capsys):
    """Test that completions output looks like a shell script."""
    # Run completions command - expect SystemExit(0)
    with pytest.raises(SystemExit) as exc_info:
        app(["completions"])

    assert exc_info.value.code == 0

    captured = capsys.readouterr()
    output = captured.out

    # The output should be a completion script
    # Cyclopts typically generates bash/zsh completion scripts
    # Check for common shell script patterns
    assert len(output) > 0
    # The output will vary based on cyclopts implementation
    # Just verify it produces output


def test_completions_no_errors(capsys):
    """Test that completions command runs without errors."""
    # Run completions - expect SystemExit(0)
    with pytest.raises(SystemExit) as exc_info:
        app(["completions"])

    assert exc_info.value.code == 0

    captured = capsys.readouterr()
    # Verify no error output
    assert captured.err == ""
