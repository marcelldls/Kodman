from . import __version__
from .engine import ArgparseEngine, Command

__all__ = ["main"]


class KockerEngine(ArgparseEngine):
    def __init__(self):
        super().__init__()
        self._parser.add_argument(
        "-v",
        "--version",
        action="version",
        version=__version__,
    )

engine = KockerEngine()

@engine.add_command
class Run(Command):

    def add(self, parser):
        parser_run = parser.add_parser('run', help='Run a command in a new container')
        parser_run.add_argument('--entrypoint', type=str, help=' Overwrite the default ENTRYPOINT of the image')
        parser_run.add_argument('--rm', help='Remove container and any anonymous unnamed volume associated with the container after exit', action="store_true")
        parser_run.add_argument('-v','--volume', type=str, help='Bind mount a volume into the container')
        parser_run.add_argument('image')
        parser_run.add_argument('command', nargs="?")
        parser_run.add_argument('args', nargs="*", default=[])

    def do(self, args):
        print(f"Image: {args.image}")
        if args.command:
            print(f"Command: {' '.join(args.command)}")
        if args.args:
            print(f"Args: {args.args}")

@engine.add_command
class Version(Command):

    def add(self, parser):
        parser.add_parser('version', help='Display the Kocker version information')

    def do(self, args):
        print(__version__)

def cli():
    engine.launch()

if __name__ == "__main__":
    cli()
