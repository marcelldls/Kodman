import argparse
import sys
from abc import ABC, abstractmethod


class Command(ABC):
    exit_code = 0

    @abstractmethod
    def do(self, args, ctx):
        pass

    @abstractmethod
    def add(self, parser):
        pass


class ArgparseEngine:
    def __init__(self):
        self._parser = argparse.ArgumentParser(description="Main program")
        self._subparsers = self._parser.add_subparsers(dest="cli_command")
        self._ctx = None
        self._args = []
        self._commands = []

    def add_command(self, command: type[Command]):
        self._commands.append(command())

    def launch(self):
        for command in self._commands:
            command.add(self._subparsers)

        args = self._parser.parse_args()

        for command in self._commands:
            if args.cli_command == command.__class__.__name__.lower():
                command.do(args, self._ctx)
                sys.exit(command.exit_code)
