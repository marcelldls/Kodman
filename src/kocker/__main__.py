import argparse

from . import __version__

__all__ = ["main"]


def cli():
    """
    # Why argparse over click/typer?
    The docker api is not POSIX compliant.
    For example: `docker run --network=host imageID dnf -y install java`
    Click/Typer does not allow this (and is correct to do so).
    They expect: `docker run --network=host imageID -- dnf -y install java`
    See Section 12.2 Guideline 10 https://pubs.opengroup.org/onlinepubs/9699919799/basedefs/V1_chap12.html#tag_12_02
    """
    parser = argparse.ArgumentParser(description='Main program')
    subparsers = parser.add_subparsers(dest='cli_command', help='command help')

    add_run(subparsers)
    add_version(subparsers)

    args = parser.parse_args()

    if args.cli_command == "run":
        do_run(args)

    if args.cli_command == "version":
        do_version(args)

def add_run(parser):
    parser_run = parser.add_parser('run', help='Run a command in a new container')
    parser_run.add_argument('--entrypoint', type=str, help=' Overwrite the default ENTRYPOINT of the image')
    parser_run.add_argument('--rm', help='Remove container and any anonymous unnamed volume associated with the container after exit', action="store_true")
    parser_run.add_argument('-v','--volume', type=str, help='Bind mount a volume into the container')
    parser_run.add_argument('image')
    parser_run.add_argument('command', nargs="?")
    parser_run.add_argument('args', nargs=argparse.REMAINDER)

def do_run(args):
    print(f"Image: {args.image}")
    if args.command:
        print(f"Command: {' '.join(args.command)}")
    if args.args:
        print(f"Args: {args.args}")

def add_version(parser):
    parser_version = parser.add_parser('version', help='Display the Kocker version information')

def do_version(args):
    print(__version__)

if __name__ == "__main__":
    cli()
