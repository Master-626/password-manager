"""Command-line interface for the generator-only prototype."""

import click

from . import __version__
from .generator import generate_password


@click.group()
@click.version_option(version=__version__)
def main():
    """Generate random passwords. Password storage is not implemented."""


@main.command(hidden=True)
@click.argument("service")
@click.option("--username", "-u", help="Legacy option; storage is unavailable.")
def add(service, username):
    """Reject the old placeholder command without asking for a password."""
    raise click.ClickException(
        "Password storage is not implemented. Nothing was saved. "
        "Use an established password manager to store credentials."
    )


@main.command(hidden=True)
@click.argument("service")
def get(service):
    """Reject the old placeholder command rather than inventing a result."""
    raise click.ClickException(
        "Password storage is not implemented. No password can be retrieved."
    )


@main.command()
@click.option(
    "--length", "-l", default=20, show_default=True,
    type=click.IntRange(8, 1024), help="Number of characters to generate.",
)
@click.option(
    "--symbols/--no-symbols", default=True, show_default=True,
    help="Include ASCII punctuation as well as letters and digits.",
)
def generate(length, symbols):
    """Print one random password. The program does not save it."""
    click.echo(generate_password(length=length, symbols=symbols))


if __name__ == "__main__":
    main()
