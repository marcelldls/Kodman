import argparse
import logging
import sys
from abc import ABC, abstractmethod

from rich.console import Console


class Command(ABC):
    exit_code = 0

    @abstractmethod
    def do(self, args, ctx, log):
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
        self._parser = argparse.ArgumentParser(description="Main program")
        self._subparsers = self._parser.add_subparsers(dest="cli_command")
        self._ctx = None
        self._args = []
        self._commands = []

    def add_command(self, command: type[Command]):
        self._commands.append(command())

    def launch(self):
        if self._status:
            self._status.start()

        for command in self._commands:
            command.add(self._subparsers)

        args = self._parser.parse_args()

        for command in self._commands:
            if args.cli_command == command.__class__.__name__.lower():
                command.do(args, self._ctx, self._log)

                if self._status:
                    self._status.stop()

                sys.exit(command.exit_code)
