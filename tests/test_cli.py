import subprocess
import sys

from kocker import __version__


def test_cli_version():
    cmd = [sys.executable, "-m", "kocker", "--version"]
    assert subprocess.check_output(cmd).decode().strip() == __version__
