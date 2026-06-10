"""Rich-powered terminal output helpers."""

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from rich import box

console = Console()

STATUS_COLORS = {
    "todo": "yellow",
    "in-progress": "blue",
    "done": "green",
}


def success(msg: str) -> None:
    console.print(f"[bold green]✔[/bold green] {msg}")


def error(msg: str) -> None:
    console.print(f"[bold red]✘[/bold red] {msg}")


def info(msg: str) -> None:
    console.print(f"[cyan]ℹ[/cyan] {msg}")


def print_users_table(users: list) -> None:
    """Render all users as a Rich table."""
    if not users:
        info("No users found.")
        return
    table = Table(title="Users", box=box.ROUNDED, header_style="bold magenta")
    table.add_column("ID", style="dim", width=5)
    table.add_column("Name", style="bold")
    table.add_column("Email")
    table.add_column("Projects", justify="right")
    for u in users:
        table.add_row(str(u.id), u.name, u.email, str(len(u.projects)))
    console.print(table)


def print_projects_table(projects: list) -> None:
    """Render a list of projects as a Rich table with inline progress bars."""
    if not projects:
        info("No projects found.")
        return
    table = Table(title="Projects", box=box.ROUNDED, header_style="bold cyan")
    table.add_column("ID", style="dim", width=5)
    table.add_column("Title", style="bold")
    table.add_column("Owner")
    table.add_column("Due Date")
    table.add_column("Tasks", justify="right")
    table.add_column("Progress")
    for p in projects:
        rate = p.completion_rate()
        table.add_row(
            str(p.id),
            p.title,
            p.owner_name or "-",
            p.due_date or "-",
            str(len(p.tasks)),
            _progress_bar(rate),
        )
    console.print(table)


def print_project_detail(project) -> None:
    """Render a full project card with its task list."""
    rate = project.completion_rate()
    header = Text(f" {project.title} ", style="bold white on blue")
    body = "\n".join([
        f"[dim]Owner:[/dim]       {project.owner_name or '-'}",
        f"[dim]Description:[/dim] {project.description or '-'}",
        f"[dim]Due Date:[/dim]    {project.due_date or '-'}",
        f"[dim]Progress:[/dim]    {_progress_bar(rate)} ({int(rate * 100)}%)",
    ])
    console.print(Panel(body, title=header, border_style="blue"))
    if not project.tasks:
        info("No tasks yet.")
        return
    table = Table(box=box.SIMPLE_HEAD, header_style="bold")
    table.add_column("ID", style="dim", width=5)
    table.add_column("Task")
    table.add_column("Status")
    table.add_column("Assigned To")
    for t in project.tasks:
        color = STATUS_COLORS.get(t.status, "white")
        table.add_row(
            str(t.id),
            t.title,
            f"[{color}]{t.status}[/{color}]",
            t.assigned_to or "-",
        )
    console.print(table)


def print_tasks_table(tasks: list) -> None:
    """Render a list of tasks as a Rich table."""
    if not tasks:
        info("No tasks found.")
        return
    table = Table(title="Tasks", box=box.ROUNDED, header_style="bold")
    table.add_column("ID", style="dim", width=5)
    table.add_column("Title", style="bold")
    table.add_column("Status")
    table.add_column("Assigned To")
    for t in tasks:
        color = STATUS_COLORS.get(t.status, "white")
        table.add_row(
            str(t.id),
            t.title,
            f"[{color}]{t.status}[/{color}]",
            t.assigned_to or "-",
        )
    console.print(table)


def _progress_bar(rate: float) -> str:
    """Return a coloured 10-block bar string for Rich markup."""
    filled = int(rate * 10)
    empty = 10 - filled
    color = "green" if rate == 1.0 else "yellow" if rate >= 0.5 else "red"
    return f"[{color}]{'█' * filled}{'░' * empty}[/{color}]"
