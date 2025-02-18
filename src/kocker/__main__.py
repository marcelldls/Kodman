import argparse
import logging

from . import __version__
from .backend import Backend, DeleteOptions, RunOptions
from .engine import ArgparseEngine, Command

log = logging.getLogger("kocker")
log.setLevel("DEBUG")
formatter = logging.Formatter("%(levelname)s:\t%(message)s")
handler = logging.StreamHandler()
handler.setFormatter(formatter)
log.addHandler(handler)


class KockerEngine(ArgparseEngine):
    def __init__(self):
        super().__init__()
        self._parser.add_argument(
            "-v",
            "--version",
            action="version",
            version=__version__,
        )
        self._ctx = Backend()


engine = KockerEngine()


@engine.add_command
class Run(Command):
    def add(self, parser):
        parser_run = parser.add_parser("run", help="Run a command in a new container")
        parser_run.add_argument(
            "--entrypoint",
            type=str,
            help=" Overwrite the default ENTRYPOINT of the image",
        )
        parser_run.add_argument(
            "--rm",
            help="Remove container and any anonymous unnamed volume associated with the container after exit",
            action="store_true",
        )
        parser_run.add_argument(
            "--volume",
            "-v",
            type=str,
            action="append",
            help="Bind mount a volume into the container",
        )
        parser_run.add_argument("image")
        parser_run.add_argument("command", nargs="?")
        parser_run.add_argument("args", nargs=argparse.REMAINDER, default=[])

    def do(self, args, ctx):
        log.debug(f"Image: {args.image}")
        pod_name = ""
        exec_command = ""
        exec_args = []
        if args.entrypoint:
            exec_command = args.entrypoint
            if args.command:
                exec_args.append(args.command)
        elif args.command:
            exec_command = args.command
        if args.args:
            exec_args += args.args

        log.debug(f"Command: {exec_command}")
        log.debug(f"Args: {exec_args}")
        exec = [exec_command] + exec_args

        options = RunOptions(
            image=args.image,
            command=exec,
            volumes=args.volume,
        )

        pod_name = ctx.run(options)
        self.exit_code = ctx.return_code
        if args.rm:
            ctx.delete(DeleteOptions(pod_name))


@engine.add_command
class Version(Command):
    def add(self, parser):
        parser.add_parser("version", help="Display the Kocker version information")

    def do(self, args, ctx):
        print(__version__)


def cli():
    engine.launch()


if __name__ == "__main__":
    cli()
