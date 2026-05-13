import typer
import time
import webbrowser
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.columns import Columns
from rich.text import Text
from rich.rule import Rule
from rich import box
from client import (
    fetch_articles,
    search_articles,
    track_keyword,
    get_digest,
    get_trending,
    export_articles,
    list_categories,
)

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
    export: str = typer.Option(None, "--export", "-e", help="Export results to CSV file path"),
):
    """Show the latest fintech news from Malaysia."""
    with console.status("[cyan]Fetching latest articles...[/cyan]"):
        articles = fetch_articles(limit=limit)
    render_articles(articles, "Latest — Fintech News Malaysia")
    if export:
        export_articles(articles, export)
        console.print(f"[green]Exported {len(articles)} articles to[/green] [bold]{export}[/bold]\n")


@app.command()
def category(
    name: str = typer.Argument(..., help="Category name (e.g. payments, blockchain, ai)"),
    limit: int = typer.Option(20, "--limit", "-n", help="Number of articles to show"),
    export: str = typer.Option(None, "--export", "-e", help="Export results to CSV file path"),
):
    """Browse articles by category."""
    cats = list_categories()
    if name not in cats:
        console.print(f"[red]Unknown category:[/red] [bold]{name}[/bold]")
        console.print(f"[dim]Available: {', '.join(cats)}[/dim]")
        raise typer.Exit(1)
    with console.status(f"[cyan]Fetching [{name}] articles...[/cyan]"):
        articles = fetch_articles(limit=limit, category=name)
    render_articles(articles, f"Category: {name.title()}")
    if export:
        export_articles(articles, export)
        console.print(f"[green]Exported {len(articles)} articles to[/green] [bold]{export}[/bold]\n")


@app.command()
def search(
    keyword: str = typer.Argument(..., help="Keyword to search for"),
    limit: int = typer.Option(20, "--limit", "-n", help="Max results to show"),
    export: str = typer.Option(None, "--export", "-e", help="Export results to CSV file path"),
):
    """Search articles by keyword."""
    with console.status(f"[cyan]Searching for '{keyword}'...[/cyan]"):
        articles = search_articles(keyword=keyword, limit=limit)
    render_articles(articles, f'Search: "{keyword}"')
    if export:
        export_articles(articles, export)
        console.print(f"[green]Exported {len(articles)} articles to[/green] [bold]{export}[/bold]\n")


@app.command()
def open(
    number: int = typer.Argument(..., help="Article number from the last list"),
    limit: int = typer.Option(20, "--limit", "-n", help="Must match the limit used in latest/search"),
):
    """Open an article by its number in your browser."""
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


@app.command()
def watch(
    interval: int = typer.Option(300, "--interval", "-i", help="Refresh interval in seconds (default: 300)"),
    limit: int = typer.Option(10, "--limit", "-n", help="Number of articles to show per refresh"),
):
    """Live feed — auto-refreshes and highlights new articles."""
    console.print(Panel(
        f"[bold cyan]Watching Fintech News Malaysia[/bold cyan]\n"
        f"[dim]Refreshing every {interval}s — press Ctrl+C to stop[/dim]",
        border_style="cyan",
    ))

    seen_links = set()

    while True:
        with console.status("[cyan]Fetching...[/cyan]"):
            articles = fetch_articles(limit=limit)

        new_articles = [a for a in articles if a["link"] not in seen_links]
        seen_links.update(a["link"] for a in articles)

        console.print(Rule(f"[dim]{__import__('datetime').datetime.now().strftime('%H:%M:%S')}[/dim]"))

        if new_articles:
            for article in new_articles:
                tags = ", ".join(article["categories"][:3]) if article["categories"] else "-"
                console.print(
                    f"[bold green]NEW[/bold green]  [white]{article['title']}[/white]\n"
                    f"      [dim]{article['date']} · {tags}[/dim]\n"
                    f"      [cyan]{article['link']}[/cyan]\n"
                )
        else:
            console.print("[dim]  No new articles since last check.[/dim]\n")

        try:
            time.sleep(interval)
        except KeyboardInterrupt:
            console.print("\n[yellow]Watch stopped.[/yellow]")
            raise typer.Exit()


@app.command()
def track(
    keyword: str = typer.Argument(..., help="Company or keyword to track (e.g. CIMB, Maybank)"),
):
    """Track mentions of a company or keyword across all articles."""
    with console.status(f"[cyan]Tracking '{keyword}'...[/cyan]"):
        result = track_keyword(keyword)

    count = result["mention_count"]
    articles = result["articles"]
    top_cats = result["top_categories"]

    if count == 0:
        console.print(f"[yellow]No mentions of '[bold]{keyword}[/bold]' found in the latest feed.[/yellow]")
        return

    console.print(Panel(
        f"[bold white]{keyword}[/bold white]\n\n"
        f"[cyan]Mentions:[/cyan] [bold green]{count}[/bold green] article(s)\n\n"
        f"[cyan]Most mentioned alongside:[/cyan]\n" +
        "\n".join(f"  [green]•[/green] {cat} [dim]({n})[/dim]" for cat, n in top_cats),
        title="[bold magenta]Keyword Tracker[/bold magenta]",
        border_style="magenta",
    ))

    table = Table(box=box.SIMPLE, show_header=True, header_style="bold cyan", expand=True)
    table.add_column("Date", style="green", width=12)
    table.add_column("Title", style="white")
    table.add_column("Tags", style="dim cyan", width=30)

    for article in articles:
        tags = ", ".join(article["categories"][:3]) if article["categories"] else "-"
        table.add_row(article["date"], article["title"], tags)

    console.print(table)


@app.command()
def digest():
    """Morning briefing — latest articles grouped by category with full content."""
    with console.status("[cyan]Preparing digest...[/cyan]"):
        data = get_digest()

    console.print(Panel(
        f"[bold white]Fintech News Malaysia[/bold white]\n[dim]{data['date']}[/dim]",
        title="[bold magenta]Daily Digest[/bold magenta]",
        border_style="magenta",
    ))

    for section, articles in data["sections"].items():
        count = len(articles)
        console.print(f"\n[bold cyan]{section.upper()}[/bold cyan] [dim]({count} article{'s' if count > 1 else ''})[/dim]")
        console.print(Rule(style="dim"))
        for article in articles:
            tags = ", ".join(t for t in article["tags"][:4] if t.lower() not in ("various", "featured")) or "-"
            console.print(f"\n  [bold white]{article['title']}[/bold white]")
            console.print(f"  [dim]{article['date']} · {tags}[/dim]")
            if article.get("summary"):
                console.print(f"  {article['summary']}\n")
            console.print(f"  [cyan]{article['link']}[/cyan]")

    console.print()


@app.command()
def trending(
    top: int = typer.Option(10, "--top", "-n", help="Number of trending topics to show"),
):
    """Show the most mentioned topics and tags right now."""
    with console.status("[cyan]Analysing trending topics...[/cyan]"):
        topics = get_trending(top_n=top)

    if not topics:
        console.print("[yellow]No trending data available.[/yellow]")
        return

    table = Table(
        box=box.ROUNDED,
        show_header=True,
        header_style="bold cyan",
        title="[bold magenta]Trending Topics — Fintech News Malaysia[/bold magenta]",
        title_justify="left",
    )
    table.add_column("Rank", style="dim", width=5, justify="right")
    table.add_column("Topic", style="white")
    table.add_column("Mentions", style="bold green", justify="right", width=10)

    for i, (topic, count) in enumerate(topics, 1):
        table.add_row(str(i), topic, str(count))

    console.print(table)


if __name__ == "__main__":
    app()
