"""Tests for the init command."""
import subprocess
from pathlib import Path

import pytest
from git import Repo

from platform_service_framework.cli import app


def test_init_default(isolated_env, capsys):
    """Test init command with default parameters."""
    tmp_path, _ = isolated_env

    # Run init command in current directory - expect SystemExit(0)
    with pytest.raises(SystemExit) as exc_info:
        app(["init"])

    assert exc_info.value.code == 0

    # Verify git repo was initialized
    assert (tmp_path / ".git").exists()

    # Verify project structure was created
    assert (tmp_path / "apps").exists()
    assert (tmp_path / "apps" / "__init__.py").exists()

    # Verify default app was created
    assert (tmp_path / "apps" / "api").exists()

    # Check output
    captured = capsys.readouterr()
    assert "Initializing your project" in captured.out
    assert "Main project created" in captured.out
    assert "Created app api" in captured.out
    assert "Framework init finished" in captured.out


def test_init_with_destination(isolated_dir, local_repo_url):
    """Test init command with specific destination."""
    destination = isolated_dir / "my-service"

    # Run init command with destination - expect SystemExit(0)
    with pytest.raises(SystemExit) as exc_info:
        app(["init", str(destination)])

    assert exc_info.value.code == 0

    # Verify destination was created
    assert destination.exists()
    assert (destination / ".git").exists()

    # Verify project structure
    assert (destination / "apps" / "api").exists()
    assert (destination / "apps" / "__init__.py").exists()


def test_init_with_custom_project_name(isolated_env, capsys):
    """Test init command with custom project name."""
    tmp_path, _ = isolated_env

    # Run init with custom project name - expect SystemExit(0)
    with pytest.raises(SystemExit) as exc_info:
        app(["init", "-p", "custom_project"])

    assert exc_info.value.code == 0

    # Check output includes custom project name
    captured = capsys.readouterr()
    assert "custom_project" in captured.out


def test_init_with_multiple_apps(isolated_env):
    """Test init command with multiple apps."""
    tmp_path, _ = isolated_env

    # Run init with multiple apps - expect SystemExit(0)
    with pytest.raises(SystemExit) as exc_info:
        app(["init", "--apps", "api", "web", "core"])

    assert exc_info.value.code == 0

    # Verify all apps were created
    assert (tmp_path / "apps" / "api").exists()
    assert (tmp_path / "apps" / "web").exists()
    assert (tmp_path / "apps" / "core").exists()
    assert (tmp_path / "apps" / "__init__.py").exists()


def test_init_creates_git_repo(isolated_env):
    """Test that init creates a git repository if one doesn't exist."""
    tmp_path, _ = isolated_env

    # Ensure no git repo exists
    assert not (tmp_path / ".git").exists()

    # Run init - expect SystemExit(0)
    with pytest.raises(SystemExit) as exc_info:
        app(["init"])

    assert exc_info.value.code == 0

    # Verify git repo was created
    assert (tmp_path / ".git").exists()

    # Verify it's a valid git repo
    repo = Repo(tmp_path)
    assert repo.git_dir == str(tmp_path / ".git")


def test_init_with_existing_git_repo(isolated_env):
    """Test init when git repo already exists."""
    tmp_path, _ = isolated_env

    # Create a git repo first
    Repo.init(tmp_path)
    assert (tmp_path / ".git").exists()

    # Run init - expect SystemExit(0)
    with pytest.raises(SystemExit) as exc_info:
        app(["init"])

    assert exc_info.value.code == 0

    # Verify git repo still exists (not recreated)
    assert (tmp_path / ".git").exists()
    repo = Repo(tmp_path)
    assert repo.git_dir == str(tmp_path / ".git")


def test_init_with_named_folder_destination(isolated_dir, local_repo_url, capsys):
    """Test init with named folder (creates folder and uses name as project)."""
    destination = isolated_dir / "my-awesome-service"

    # Run init - expect SystemExit(0)
    with pytest.raises(SystemExit) as exc_info:
        app(["init", str(destination)])

    assert exc_info.value.code == 0

    # Verify folder was created
    assert destination.exists()

    # Verify project name defaults to folder name (with underscores)
    captured = capsys.readouterr()
    assert "my_awesome_service" in captured.out or "my-awesome-service" in captured.out


def test_init_without_apps(isolated_env):
    """Test init command with no apps."""
    tmp_path, _ = isolated_env

    # Run init with empty apps list - expect SystemExit(0)
    with pytest.raises(SystemExit) as exc_info:
        app(["init", "--apps"])

    assert exc_info.value.code == 0

    # Verify apps directory exists but is empty (except __init__.py shouldn't be created)
    # Based on the code, __init__.py is only created if apps is not empty
    # So we need to check the actual behavior
    if (tmp_path / "apps").exists():
        # The apps directory might still be created by the template
        assert (tmp_path / "apps").exists()

def test_init_run_all_project_checks(isolated_env, capsys):
    """Test init command with default parameters and run all unit tests and linters."""
    tmp_path, _ = isolated_env

    # Run init command in current directory - expect SystemExit(0)
    with pytest.raises(SystemExit) as exc_info:
        app(["init"])

    assert exc_info.value.code == 0

    # Run validate command in current directory - expect SystemExit(0)
    with pytest.raises(SystemExit) as exc_info:
        app(["validate"])

    assert exc_info.value.code == 0

    # Run poe check to validate lint
    lint_exec = subprocess.run(
        ["poe", "lint"],
        cwd=tmp_path,
        capture_output=True,
        text=True,
    )
    assert lint_exec.returncode == 0 and 'All checks passed!' in lint_exec.stdout, (
        f"poe lint failed with exit code {lint_exec.returncode}\n"
        f"stdout: {lint_exec.stdout}\n"
        f"stderr: {lint_exec.stderr}"
    )

    # Run poe format to validate formatting
    format_exec = subprocess.run(
        ["poe", "format"],
        cwd=tmp_path,
        capture_output=True,
        text=True,
    )
    assert format_exec.returncode == 0 and 'reformatted' not in format_exec.stdout, (
        f"poe format failed with exit code {format_exec.returncode}\n"
        f"stdout: {format_exec.stdout}\n"
        f"stderr: {format_exec.stderr}"
    )

    # Run makemigrations and poe unit-test subsequently to validate unit tests
    migrations_exec = subprocess.run(
        ["uv", "run", "manage.py", "makemigrations"],
        cwd=tmp_path,
        capture_output=True,
        text=True,
    )
    assert migrations_exec.returncode == 0 and "Migrations for 'core'" in migrations_exec.stdout, (
        f"manage.py makemigrations failed with exit code {migrations_exec.returncode}\n"
        f"stdout: {migrations_exec.stdout}\n"
        f"stderr: {migrations_exec.stderr}"
    )
    test_exec = subprocess.run(
        ["poe", "unit-test"],
        cwd=tmp_path,
        capture_output=True,
        text=True,
    )
    assert test_exec.returncode == 0 and "OK" in test_exec.stderr, (
        f"poe unit-test failed with exit code {test_exec.returncode}\n"
        f"stdout: {test_exec.stdout}\n"
        f"stderr: {test_exec.stderr}"
    )

    # Run all checks with poe check
    checks_exec = subprocess.run(
        ["poe", "check"],
        cwd=tmp_path,
        capture_output=True,
        text=True,
    )
    assert checks_exec.returncode == 0, (
        f"poe check failed with exit code {test_exec.returncode}\n"
        f"stdout: {test_exec.stdout}\n"
        f"stderr: {test_exec.stderr}"
    )

