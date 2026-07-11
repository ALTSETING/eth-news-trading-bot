from datetime import datetime
from rich.console import Console
from rich.live import Live
from rich.table import Table
from rich.panel import Panel
from database import latest_news, total_count

console = Console()


def build_screen(status: dict):
    table = Table(expand=True)
    table.add_column("Час", width=8)
    table.add_column("Категорія", width=23)
    table.add_column("Score", justify="right", width=7)
    table.add_column("Важл.", justify="right", width=7)
    table.add_column("Conf.", justify="right", width=7)
    table.add_column("Рішення", width=10)
    table.add_column("Новина")

    for row in latest_news():
        created = str(row["created_at"] or "")[-8:]
        table.add_row(
            created,
            row["category"] or "-",
            str(row["score"] if row["score"] is not None else "-"),
            str(row["importance"] if row["importance"] is not None else "-"),
            str(row["confidence"] if row["confidence"] is not None else "-"),
            row["action"] or "-",
            row["title"][:90],
        )

    header = (
        f"[bold]ETH NEWS PAPER BOT[/bold]\n"
        f"Час: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | "
        f"Статус: {status.get('state', 'starting')} | "
        f"У базі: {total_count()} | "
        f"Черга: {status.get('queue', 0)} | "
        f"Остання помилка: {status.get('error', '-')}"
    )

    return Panel.fit(header, title="Стан") , table


def render_loop(status: dict, stop_event, refresh_seconds: float = 1):
    with Live(console=console, refresh_per_second=4, screen=False) as live:
        while not stop_event.is_set():
            header, table = build_screen(status)
            from rich.console import Group
            live.update(Group(header, table))
            stop_event.wait(refresh_seconds)
