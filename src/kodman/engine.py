import argparse
import logging
import sys
from abc import ABC, abstractmethod
from typing import overload

from rich.console import Console

from .utilities import get_env as _get_env


class Command(ABC):
    exit_code = 0

    @abstractmethod
    def do(self, args, ctx, env, log):
        pass

    @abstractmethod
    def add(self, parser):
        pass


class ConsoleOutputHandler(logging.Handler):
    def __init__(self, status):
        super().__init__()
        self._status = status

    def emit(self, record):
        self._status.update(record.msg)


class ArgparseEngine:
    _env_types = {}
    _env_vals = {}

    def __init__(self, debug=False):
        # Configure logging
        self._log = logging.getLogger("ArgparseEngine")
        self._console = Console()
        self._status = None
        if debug:
            formatter = logging.Formatter("%(levelname)s:\t%(message)s")
            handler = logging.StreamHandler()
            handler.setFormatter(formatter)
            self._log.addHandler(handler)
            self._log.setLevel("DEBUG")
        else:
            self._status = self._console.status("Initializing application...")
            handler = ConsoleOutputHandler(self._status)
            self._log.addHandler(handler)
            self._log.setLevel("INFO")

        # Configure application
        self._parser = argparse.ArgumentParser(
            formatter_class=argparse.RawTextHelpFormatter,
        )
        self._subparsers = self._parser.add_subparsers(dest="cli_command")
        self._ctx = None
        self._args = []
        self._commands = []

    def add_command(self, command: type[Command]):
        self._commands.append(command())

    @overload
    def get_env(self, variable: str, expected_type: type[bool]) -> bool | None: ...

    @overload
    def get_env(self, variable: str, expected_type: type[int]) -> int | None: ...

    @overload
    def get_env(self, variable: str, expected_type: type[str]) -> str | None: ...

    def get_env(
        self, variable: str, expected_type: type[bool | int | str]
    ) -> bool | int | str | None:
        val = _get_env(variable, expected_type)
        self._env_types[variable] = expected_type
        self._env_vals[variable] = val

        return val

    def _process_env(self):
        message = "environment variables:\n"
        for env, _type in self._env_types.items():
            message_prefix = f"  {env}  {_type.__name__}"
            message_body = (
                f"  (current: {self._env_vals[env]})" if self._env_vals[env] else ""
            )
            message_suffix = "\n"
            message += message_prefix + message_body + message_suffix
        self._parser.epilog = message

    def launch(self):
        for command in self._commands:
            command.add(self._subparsers)

        self._process_env()

        args = self._parser.parse_args()

        if self._status:
            self._status.start()

        for command in self._commands:
            if args.cli_command == command.__class__.__name__.lower():
                command.do(args, self._ctx, self._env_vals, self._log)

                if self._status:
                    self._status.stop()

                sys.exit(command.exit_code)
