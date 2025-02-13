"""Interface for ``python -m kocker``."""

from typing import Optional

from . import __version__

__all__ = ["main"]

import typer


def version_callback(value: bool):
    if value:
        typer.echo(__version__)
        raise typer.Exit()


cli = typer.Typer()

@cli.callback()
def main(
    ctx: typer.Context,
    version: Optional[bool] = typer.Option(  # noqa (Optional required for typer)
        None,
        "--version",
        callback=version_callback,
        is_eager=True,
        help="Log the version of kocker",
    ),):
    pass

@cli.command()
def version(name: str):
    """Log the version of kocker"""
    typer.echo(__version__)

if __name__ == "__main__":
    cli()
