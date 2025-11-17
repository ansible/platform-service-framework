"""Tests for the validate command."""

from pathlib import Path

import pytest

from platform_service_framework.cli import app


def test_validate_default_destination(isolated_env, capsys):
    """Test validate command with default destination (current directory)."""
    tmp_path, _ = isolated_env

    # Run validate command - expect SystemExit(0)
    with pytest.raises(SystemExit) as exc_info:
        app(["validate"])

    assert exc_info.value.code == 0

    # Check output
    captured = capsys.readouterr()
    assert "Validating your app" in captured.out
    assert str(tmp_path) in captured.out


def test_validate_with_specific_destination(isolated_dir, local_repo_url, capsys):
    """Test validate command with specific destination."""
    destination = isolated_dir / "my-service"
    destination.mkdir()

    # Run validate with destination - expect SystemExit(0)
    with pytest.raises(SystemExit) as exc_info:
        app(["validate", str(destination)])

    assert exc_info.value.code == 0

    # Check output
    captured = capsys.readouterr()
    assert "Validating your app" in captured.out
    assert str(destination) in captured.out


def test_validate_on_initialized_project(isolated_env, capsys):
    """Test validate on an initialized project."""
    tmp_path, _ = isolated_env

    # First initialize a project - expect SystemExit(0)
    with pytest.raises(SystemExit) as exc_info:
        app(["init"])
    assert exc_info.value.code == 0

    # Clear the captured output
    capsys.readouterr()

    # Run validate - expect SystemExit(0)
    with pytest.raises(SystemExit) as exc_info:
        app(["validate"])

    assert exc_info.value.code == 0

    # Check output
    captured = capsys.readouterr()
    assert "Validating your app" in captured.out
