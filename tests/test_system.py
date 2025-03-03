import os
import subprocess
from pathlib import Path

import pytest

from data import responses

ENTRY_POINT = "kodman"
DOCKER_PROVIDER = os.getenv("DOCKER_PROVIDER", "podman")
KODMAN_SYSTEM_TESTING = os.getenv("KODMAN_SYSTEM_TESTING") == "true"


@pytest.mark.skipif(
    not KODMAN_SYSTEM_TESTING, reason="export KODMAN_SYSTEM_TESTING=true"
)
def remove_empty_lines(text):
    """Remove after solving https://github.com/epics-containers/Kodman/issues/9"""
    lines = [line for line in text.split("\n") if line.strip()]
    return "\n".join(lines)


@pytest.mark.skipif(
    not KODMAN_SYSTEM_TESTING, reason="export KODMAN_SYSTEM_TESTING=true"
)
def test_docker_run_hello():
    cmd = [DOCKER_PROVIDER, "run", "--rm", "hello-world"]
    assert subprocess.check_output(cmd).decode().strip() == responses.hello_world


@pytest.mark.skipif(
    not KODMAN_SYSTEM_TESTING, reason="export KODMAN_SYSTEM_TESTING=true"
)
def test_kodman_run_hello():
    cmd = [ENTRY_POINT, "run", "--rm", "hello-world"]
    assert subprocess.check_output(cmd).decode().strip() == remove_empty_lines(
        responses.hello_world
    )


@pytest.mark.skipif(
    not KODMAN_SYSTEM_TESTING, reason="export KODMAN_SYSTEM_TESTING=true"
)
def test_docker_run_exitcodes():
    ERROR_MSG = "My error message"
    cmd = [
        DOCKER_PROVIDER,
        "run",
        "--entrypoint",
        "bash",
        "--rm",
        "ubuntu",
        "-c",
        f"echo '{ERROR_MSG}' >&2; exit 1",
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)
    assert result.returncode == 1
    assert result.stderr.strip() == ERROR_MSG


@pytest.mark.skipif(
    not KODMAN_SYSTEM_TESTING, reason="export KODMAN_SYSTEM_TESTING=true"
)
def test_kodman_run_exitcodes():
    ERROR_MSG = "My error message"
    cmd = [
        ENTRY_POINT,
        "run",
        "--entrypoint",
        "bash",
        "--rm",
        "ubuntu",
        "-c",
        f"echo '{ERROR_MSG}' >&2; exit 1",
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)
    assert result.returncode == 1
    assert (
        result.stdout.strip() == ERROR_MSG
    )  # K8s does not distinguish between stderr and stdout!


@pytest.mark.skipif(
    not KODMAN_SYSTEM_TESTING, reason="export KODMAN_SYSTEM_TESTING=true"
)
def test_docker_run_mount(data: Path):
    FILE_MOUNT = "to_mount.txt"
    cmd = [
        DOCKER_PROVIDER,
        "run",
        "-v",
        f"{data}:/test",
        "--rm",
        "ubuntu",
        "bash",
        "-c",
        f"cat test/{FILE_MOUNT}",
    ]

    assert subprocess.check_output(cmd).decode().strip() == responses.mount


@pytest.mark.skipif(
    not KODMAN_SYSTEM_TESTING, reason="export KODMAN_SYSTEM_TESTING=true"
)
def test_kodman_run_mount(data: Path):
    FILE_MOUNT = "to_mount.txt"
    cmd = [
        ENTRY_POINT,
        "run",
        "-v",
        f"{data}:/test",
        "--rm",
        "ubuntu",
        "bash",
        "-c",
        f"cat test/{FILE_MOUNT}",
    ]

    assert subprocess.check_output(cmd).decode().strip() == responses.mount


@pytest.mark.skipif(
    not KODMAN_SYSTEM_TESTING, reason="export KODMAN_SYSTEM_TESTING=true"
)
def test_kodman_fail_image(data: Path):
    cmd = [
        ENTRY_POINT,
        "run",
        "--rm",
        "hello-worl",
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)
    assert result.returncode == 1


@pytest.mark.skipif(
    not KODMAN_SYSTEM_TESTING, reason="export KODMAN_SYSTEM_TESTING=true"
)
def test_kodman_fail_command(data: Path):
    cmd = [
        ENTRY_POINT,
        "run",
        "--rm",
        "--entrypoint",
        "bash",
        "hello-world",
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)
    assert result.returncode == 1
    assert result.stderr.strip() == responses.failed_command
