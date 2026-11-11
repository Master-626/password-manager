"""Command-line interface for the generator-only prototype."""

import click

from . import __version__
from .generator import generate_password

# Click appends one of these when it can suggest a real option or command.
# Keep the suggestion, drop the token the user typed: it may be a password.
_SUGGESTION_MARKERS = (
    "(Did you mean",
    "(Possible options:",
    "Did you mean",
)


def _suggestion_suffix(message):
    indexes = [message.find(marker) for marker in _SUGGESTION_MARKERS]
    indexes = [index for index in indexes if index != -1]
    if not indexes:
        return ""
    return " " + message[min(indexes) :]


def _redact_usage_error(exc):
    """Return a message that omits user text, or None to keep ``exc``."""
    no_such_command = getattr(click, "NoSuchCommand", None)
    if isinstance(exc, click.NoSuchOption):
        return "No such option." + _suggestion_suffix(exc.format_message())
    if no_such_command is not None and isinstance(exc, no_such_command):
        return "No such command." + _suggestion_suffix(exc.format_message())

    message = exc.format_message()
    if message.startswith("Got unexpected extra argument"):
        return (
            "Got unexpected extra arguments. "
            "Their text was hidden in case a secret was included."
        )
    # Click before 8.4 raises a plain UsageError for an unknown command.
    if message.startswith("No such command "):
        return "No such command." + _suggestion_suffix(message)
    return None


class _RedactingMixin:
    def parse_args(self, ctx, args):
        try:
            return super().parse_args(ctx, args)
        except click.UsageError as exc:
            redacted = _redact_usage_error(exc)
            if redacted is None:
                raise
            raise click.UsageError(redacted, ctx=exc.ctx) from None


class _RedactingCommand(_RedactingMixin, click.Command):
    pass


class _RedactingGroup(_RedactingMixin, click.Group):
    command_class = _RedactingCommand

    def resolve_command(self, ctx, args):
        try:
            return super().resolve_command(ctx, args)
        except click.UsageError as exc:
            redacted = _redact_usage_error(exc)
            if redacted is None:
                raise
            raise click.UsageError(redacted, ctx=exc.ctx) from None


@click.group(cls=_RedactingGroup)
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
    "--length",
    "-l",
    default=20,
    show_default=True,
    type=click.IntRange(8, 1024),
    help="Number of characters to generate.",
)
@click.option(
    "--symbols/--no-symbols",
    default=True,
    show_default=True,
    help="Include ASCII punctuation as well as letters and digits.",
)
@click.option(
    "--count",
    "-n",
    default=1,
    show_default=True,
    type=click.IntRange(1, 100),
    help="How many passwords to print, one per line.",
)
def generate(length, symbols, count):
    """Print random passwords. The program does not save them."""
    try:
        passwords = [
            generate_password(length=length, symbols=symbols) for _ in range(count)
        ]
    except RuntimeError as exc:
        raise click.ClickException(str(exc)) from exc
    # color=True keeps the characters exactly. Otherwise Click strips text that
    # looks like ANSI color when stdout is not a terminal (pipes and captures).
    click.echo("\n".join(passwords), color=True)


if __name__ == "__main__":
    main()
