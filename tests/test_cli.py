import subprocess
import sys

from kodman import __version__


def test_cli_version():
    cmd = [sys.executable, "-m", "kodman", "--version"]
    assert subprocess.check_output(cmd).decode().strip() == __version__
