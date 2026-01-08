"""Console output utilities using Rich."""

from rich.console import Console
from rich.table import Table

console = Console()


def success(msg: str):
    """Print success message."""
    console.print(f"[green]\u2713[/green] {msg}")


def error(msg: str):
    """Print error message."""
    console.print(f"[red]\u2717[/red] {msg}")


def warning(msg: str):
    """Print warning message."""
    console.print(f"[yellow]![/yellow] {msg}")


def info(msg: str):
    """Print info message."""
    console.print(f"[blue]\u2192[/blue] {msg}")


def header(msg: str):
    """Print section header."""
    console.print(f"\n[bold]==> {msg}[/bold]")


def dim(msg: str):
    """Print dimmed text."""
    console.print(f"[dim]{msg}[/dim]")


def create_table(*columns: str) -> Table:
    """Create a table with given columns."""
    table = Table(show_header=True, header_style="bold")
    for col in columns:
        table.add_column(col)
    return table
