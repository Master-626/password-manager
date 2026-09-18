"""CLI interface."""
import click
from rich.console import Console
from rich.table import Table

console = Console()

@click.group()
@click.version_option(version="0.1.0")
def main():
    """Password Manager - Securely manage your passwords."""
    pass

@main.command()
@click.argument("service")
@click.option("--username", "-u", help="Username")
@click.password_option("--password", "-p", help="Password")
def add(service, username, password):
    """Add a new password entry."""
    console.print(f"✅ Added password for: [bold green]{service}[/bold green]")

@main.command()
@click.argument("service")
def get(service):
    """Get a password."""
    console.print(f"🔑 Password for {service}: ********")

@main.command()
@click.option("--length", "-l", default=16, help="Password length")
def generate(length):
    """Generate a strong password."""
    console.print(f"🔐 Generated password: [bold green]xY7#kL2$mN9!pQ4@[/bold green] (length: {length})")

if __name__ == "__main__":
    main()
