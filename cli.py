import typer
import webbrowser
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from rich import box
from client import fetch_articles, search_articles, list_categories

app = typer.Typer(
    name="fnews",
    help="Fintech News Malaysia — terminal edition.",
    add_completion=False,
)
console = Console()


def render_articles(articles: list[dict], title: str):
    if not articles:
        console.print("[yellow]No articles found.[/yellow]")
        return

    table = Table(
        box=box.ROUNDED,
        show_header=True,
        header_style="bold cyan",
        title=f"[bold magenta]{title}[/bold magenta]",
        title_justify="left",
        expand=True,
    )
    table.add_column("#", style="dim", width=3, justify="right")
    table.add_column("Date", style="green", width=12)
    table.add_column("Title", style="white")
    table.add_column("Tags", style="dim cyan", width=30)

    for i, article in enumerate(articles, 1):
        tags = ", ".join(article["categories"][:3]) if article["categories"] else "-"
        table.add_row(str(i), article["date"], article["title"], tags)

    console.print(table)
    console.print(f"[dim]  {len(articles)} article(s) — use [bold]fnews open <#>[/bold] to read in browser[/dim]\n")


@app.command()
def latest(
    limit: int = typer.Option(20, "--limit", "-n", help="Number of articles to show"),
):
    """Show the latest fintech news from Malaysia."""
    with console.status("[cyan]Fetching latest articles...[/cyan]"):
        articles = fetch_articles(limit=limit)
    render_articles(articles, "Latest — Fintech News Malaysia")


@app.command()
def category(
    name: str = typer.Argument(..., help="Category name (e.g. payments, blockchain, ai)"),
    limit: int = typer.Option(20, "--limit", "-n", help="Number of articles to show"),
):
    """Browse articles by category."""
    categories = list_categories()
    if name not in categories:
        console.print(f"[red]Unknown category:[/red] [bold]{name}[/bold]")
        console.print(f"[dim]Available: {', '.join(categories)}[/dim]")
        raise typer.Exit(1)
    with console.status(f"[cyan]Fetching [{name}] articles...[/cyan]"):
        articles = fetch_articles(limit=limit, category=name)
    render_articles(articles, f"Category: {name.title()}")


@app.command()
def search(
    keyword: str = typer.Argument(..., help="Keyword to search for"),
    limit: int = typer.Option(20, "--limit", "-n", help="Max results to show"),
):
    """Search articles by keyword."""
    with console.status(f"[cyan]Searching for '{keyword}'...[/cyan]"):
        articles = search_articles(keyword=keyword, limit=limit)
    render_articles(articles, f'Search: "{keyword}"')


@app.command()
def open(
    number: int = typer.Argument(..., help="Article number from the last list"),
    limit: int = typer.Option(20, "--limit", "-n", help="Must match the limit used in latest/search"),
):
    """Open an article by its number (from latest or category list)."""
    with console.status("[cyan]Fetching articles...[/cyan]"):
        articles = fetch_articles(limit=limit)
    if number < 1 or number > len(articles):
        console.print(f"[red]Invalid number. Choose between 1 and {len(articles)}.[/red]")
        raise typer.Exit(1)
    article = articles[number - 1]
    console.print(Panel(
        f"[bold white]{article['title']}[/bold white]\n\n"
        f"[dim]{article['date']} · {article['author']}[/dim]\n\n"
        f"{article['summary']}...\n\n"
        f"[cyan]{article['link']}[/cyan]",
        title="Opening in browser",
        border_style="magenta",
    ))
    webbrowser.open(article["link"])


@app.command()
def categories():
    """List all available categories."""
    cats = list_categories()
    console.print("\n[bold cyan]Available categories:[/bold cyan]\n")
    for cat in cats:
        console.print(f"  [green]•[/green] {cat}")
    console.print(f"\n[dim]Usage: fnews category <name>[/dim]\n")


if __name__ == "__main__":
    app()
