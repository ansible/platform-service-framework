"""Tests for the update command."""

from pathlib import Path
from unittest.mock import ANY, patch

import pytest
from git import Repo

from platform_service_framework.cli import app


def test_update_default_destination(isolated_env, capsys, local_repo_url):
    """Test update command with default destination (current directory)."""
    tmp_path, _ = isolated_env

    # First initialize a project - expect SystemExit(0)
    with pytest.raises(SystemExit) as exc_info:
        app(["init"])
    assert exc_info.value.code == 0

    # Mock run_update to avoid actual copier execution
    with (
        patch("platform_service_framework.cli.run_update") as mock_update,
        patch("platform_service_framework.cli._update_managed_app") as mock_app_update,
    ):
        # Run update command - expect SystemExit(0)
        with pytest.raises(SystemExit) as exc_info:
            app(["update"])

        assert exc_info.value.code == 0

        # Verify run_update was called with correct parameters
        mock_update.assert_called_once_with(
            tmp_path,
            vcs_ref=ANY,  # Branch name from local repo
            overwrite=True,
            skip_answered=True,
        )
        assert mock_app_update.call_count == 2

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
    with (
        patch("platform_service_framework.cli.run_update") as mock_update,
        patch("platform_service_framework.cli._update_managed_app") as mock_app_update,
    ):
        # Run update with destination - expect SystemExit(0)
        with pytest.raises(SystemExit) as exc_info:
            app(["update", str(destination)])

        assert exc_info.value.code == 0

        # Verify run_update was called
        mock_update.assert_called_once_with(
            destination,
            vcs_ref=ANY,  # Branch name from local repo
            overwrite=True,
            skip_answered=True,
        )
        assert mock_app_update.call_count == 2

    # Check output
    captured = capsys.readouterr()
    assert "Updating your app" in captured.out
    assert str(destination) in captured.out


def test_update_updates_all_managed_apps(isolated_env):
    """Test that update invokes the template update for every managed app."""
    tmp_path, _ = isolated_env
    repo = Repo.init(tmp_path)
    (tmp_path / ".copier-answers.yml").write_text(
        "_commit: test\n_src_path: /tmp/template\nsrc_branch: devel\n"
    )
    for app_name in ("core", "metrics"):
        app_path = tmp_path / "apps" / app_name
        app_path.mkdir(parents=True)
        (app_path / ".copier-answers.yml").write_text(
            f"_commit: test\n_src_path: /tmp/template\nsrc_branch: devel\n"
            f"app_name: {app_name}\n"
        )
    repo.index.add([".copier-answers.yml"])
    repo.index.add(["apps"])
    repo.index.commit("Initialize test project")

    with (
        patch(
            "platform_service_framework.cli.get_repo",
            return_value=(str(Path(__file__).parent.parent), None),
        ),
        patch("platform_service_framework.cli.validate", return_value=True),
    ):
        with (
            patch("platform_service_framework.cli.run_update"),
            patch("platform_service_framework.cli._update_managed_app") as update_app,
        ):
            with pytest.raises(SystemExit) as exc_info:
                app(["update", "--core"])

    assert exc_info.value.code == 0
    assert update_app.call_count == 2
    updated_paths = {call.args[1] for call in update_app.call_args_list}
    assert updated_paths == {tmp_path / "apps" / "core", tmp_path / "apps" / "metrics"}


def test_update_non_git_repository(isolated_env, capsys):
    """Test that update command triggers an error in case it is executed in a non-git repository."""
    tmp_path, _ = isolated_env

    # Create a .copier-answers.yml to get past the initial check
    answers_file = tmp_path / ".copier-answers.yml"
    answers_file.write_text("_src_path: /some/path\n")

    # Run update - expect SystemExit(1)
    with pytest.raises(SystemExit) as exc_info:
        app(["update"])

    assert exc_info.value.code == 1

    # Check output (now comes from validate command)
    captured = capsys.readouterr()
    assert "Updating your app" in captured.out
    assert (
        "Platform service framework is only supported in git-tracked repositories" in captured.out
    )
    assert "Validation failed" in captured.out


def test_update_dirty_git_repository(isolated_env, capsys):
    """Test that update command triggers an error when repository has uncommitted changes."""
    tmp_path, _ = isolated_env

    # First initialize a project - expect SystemExit(0)
    with pytest.raises(SystemExit) as exc_info:
        app(["init"])
    assert exc_info.value.code == 0

    # Make changes to create a dirty state
    test_file = tmp_path / "test_file.txt"
    test_file.write_text("Some uncommitted change")

    # Run update - expect SystemExit(1)
    with pytest.raises(SystemExit) as exc_info:
        app(["update"])

    assert exc_info.value.code == 1

    # Check output
    captured = capsys.readouterr()
    assert "Updating your app" in captured.out
    assert "Working tree has uncommitted changes" in captured.out
    assert "Please commit or stash your changes before running update" in captured.out
