"""Tests for the update command."""

from pathlib import Path
from unittest.mock import patch

import pytest

from platform_service_framework.cli import app


def test_update_default_destination(isolated_env, capsys):
    """Test update command with default destination (current directory)."""
    tmp_path, _ = isolated_env

    # First initialize a project - expect SystemExit(0)
    with pytest.raises(SystemExit) as exc_info:
        app(["init"])
    assert exc_info.value.code == 0

    # Mock run_update to avoid actual copier execution
    with patch("platform_service_framework.cli.run_update") as mock_update:
        # Run update command - expect SystemExit(0)
        with pytest.raises(SystemExit) as exc_info:
            app(["update"])

        assert exc_info.value.code == 0

        # Verify run_update was called with correct parameters
        mock_update.assert_called_once_with(
            tmp_path,
            overwrite=True,
            skip_answered=True,
        )

    # Check output
    captured = capsys.readouterr()
    assert "Updating your app" in captured.out
    assert str(tmp_path) in captured.out


def test_update_with_specific_destination(isolated_dir, local_repo_url, capsys):
    """Test update command with specific destination."""
    destination = isolated_dir / "my-service"

    # First initialize a project - expect SystemExit(0)
    with pytest.raises(SystemExit) as exc_info:
        app(["init", str(destination)])
    assert exc_info.value.code == 0

    # Mock run_update
    with patch("platform_service_framework.cli.run_update") as mock_update:
        # Run update with destination - expect SystemExit(0)
        with pytest.raises(SystemExit) as exc_info:
            app(["update", str(destination)])

        assert exc_info.value.code == 0

        # Verify run_update was called
        mock_update.assert_called_once_with(
            destination,
            overwrite=True,
            skip_answered=True,
        )

    # Check output
    captured = capsys.readouterr()
    assert "Updating your app" in captured.out
    assert str(destination) in captured.out


def test_update_parameters(isolated_env):
    """Test that update command passes correct parameters to run_update."""
    tmp_path, _ = isolated_env

    with patch("platform_service_framework.cli.run_update") as mock_update:
        # Run update - expect SystemExit(0)
        with pytest.raises(SystemExit) as exc_info:
            app(["update"])

        assert exc_info.value.code == 0

        # Verify the parameters passed to run_update
        call_args = mock_update.call_args
        assert call_args.kwargs["overwrite"] is True
        assert call_args.kwargs["skip_answered"] is True
