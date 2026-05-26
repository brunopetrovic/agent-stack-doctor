"""Tests for the CLI entrypoint."""

import subprocess
import sys


def test_cli_help():
    result = subprocess.run(
        [sys.executable, "-m", "agent_doctor.cli", "--help"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr
    assert "agent-doctor" in result.stdout


def test_credentials_command_help():
    result = subprocess.run(
        [sys.executable, "-m", "agent_doctor.cli", "credentials", "--help"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr


def test_routing_command_help():
    result = subprocess.run(
        [sys.executable, "-m", "agent_doctor.cli", "routing", "--help"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr


def test_cron_command_help():
    result = subprocess.run(
        [sys.executable, "-m", "agent_doctor.cli", "cron", "--help"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr


def test_memory_command_help():
    result = subprocess.run(
        [sys.executable, "-m", "agent_doctor.cli", "memory", "--help"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr


def test_skills_command_help():
    result = subprocess.run(
        [sys.executable, "-m", "agent_doctor.cli", "skills", "--help"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr


def test_credentials_finds_placeholder(tmp_path):
    env_file = tmp_path / ".env"
    env_file.write_text("STRIPE_KEY='Fake'\nOPENAI_API_KEY=sk-real-key\n")
    result = subprocess.run(
        [sys.executable, "-m", "agent_doctor.cli", "credentials", "--env-file", str(env_file)],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 1
    assert "STRIPE_KEY" in result.stdout


def test_scan_nonexistent_root():
    result = subprocess.run(
        [sys.executable, "-m", "agent_doctor.cli", "scan", "--root", "/nonexistent/path/123"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 1
    assert "does not exist" in result.stderr