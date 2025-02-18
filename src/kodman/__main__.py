import argparse
import logging

from . import __version__
from .backend import Backend, DeleteOptions, RunOptions
from .engine import ArgparseEngine, Command

log = logging.getLogger("kodman")
log.setLevel("DEBUG")
formatter = logging.Formatter("%(levelname)s:\t%(message)s")
handler = logging.StreamHandler()
handler.setFormatter(formatter)
log.addHandler(handler)


class kodmanEngine(ArgparseEngine):
    def __init__(self):
        super().__init__()
        self._parser.add_argument(
            "-v",
            "--version",
            action="version",
            version=__version__,
        )
        self._ctx = Backend()


engine = kodmanEngine()


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
        ctx.connect()
        log.debug(f"Image: {args.image}")
        pod_name = ""
        k8s_command = []
        k8s_args = []
        if args.entrypoint:
            k8s_command = [args.entrypoint]
        if args.command:
            k8s_args.append(args.command)
        if args.args:
            k8s_args += args.args

        log.debug(f"Command: {k8s_command}")
        log.debug(f"Args: {k8s_args}")

        options = RunOptions(
            image=args.image,
            command=k8s_command,
            args=k8s_args,
            volumes=args.volume,
        )

        pod_name = ctx.run(options)
        self.exit_code = ctx.return_code
        if args.rm:
            ctx.delete(DeleteOptions(pod_name))


@engine.add_command
class Version(Command):
    def add(self, parser):
        parser.add_parser("version", help="Display the kodman version information")

    def do(self, args, ctx):
        print(__version__)


def cli():
    engine.launch()


if __name__ == "__main__":
    cli()
