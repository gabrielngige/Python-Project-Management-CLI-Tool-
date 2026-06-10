"""Project model — owns a list of Tasks and belongs to a User."""

from __future__ import annotations
from datetime import datetime
from models.task import Task


class Project:
    """A named initiative owned by one user, containing ordered tasks."""

    _id_counter: int = 1

    def __init__(
        self,
        title: str,
        description: str = "",
        due_date: str | None = None,
        owner_name: str | None = None,
    ) -> None:
        self.id = Project._id_counter
        Project._id_counter += 1
        self.title = title              # setter validates
        self.description = description
        self.due_date = due_date        # setter validates format
        self.owner_name = owner_name
        self._tasks: list[Task] = []

    # ── title ──────────────────────────────────────────────────────────────────

    @property
    def title(self) -> str:
        return self._title

    @title.setter
    def title(self, value: str) -> None:
        if not value or not value.strip():
            raise ValueError("Project title cannot be empty.")
        self._title = value.strip()

    # ── description ────────────────────────────────────────────────────────────

    @property
    def description(self) -> str:
        return self._description

    @description.setter
    def description(self, value: str) -> None:
        self._description = value or ""

    # ── due_date ───────────────────────────────────────────────────────────────

    @property
    def due_date(self) -> str | None:
        return self._due_date

    @due_date.setter
    def due_date(self, value: str | None) -> None:
        if value:
            try:
                datetime.strptime(value, "%Y-%m-%d")
            except ValueError:
                raise ValueError(f"due_date must be YYYY-MM-DD, got: {value!r}")
        self._due_date = value

    # ── tasks (read-only collection) ───────────────────────────────────────────

    @property
    def tasks(self) -> list[Task]:
        return list(self._tasks)

    def add_task(self, task: Task) -> None:
        self._tasks.append(task)

    def remove_task(self, task: Task) -> None:
        self._tasks.remove(task)

    def find_task(self, title: str) -> Task | None:
        """Case-insensitive lookup by title."""
        return next(
            (t for t in self._tasks if t.title.lower() == title.lower()), None
        )

    # ── metrics ────────────────────────────────────────────────────────────────

    def completion_rate(self) -> float:
        """Return fraction of tasks marked done (0.0 if no tasks)."""
        if not self._tasks:
            return 0.0
        done = sum(1 for t in self._tasks if t.status == "done")
        return done / len(self._tasks)

    # ── serialisation ──────────────────────────────────────────────────────────

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "due_date": self.due_date,
            "owner_name": self.owner_name,
            "tasks": [t.to_dict() for t in self._tasks],
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Project":
        project = cls(
            data["title"],
            data.get("description", ""),
            data.get("due_date"),
            data.get("owner_name"),
        )
        project.id = data.get("id", project.id)
        for task_data in data.get("tasks", []):
            project.add_task(Task.from_dict(task_data))
        return project

    def __str__(self) -> str:
        return (
            f"Project: {self._title} | Owner: {self.owner_name} "
            f"| Tasks: {len(self._tasks)}"
        )

    def __repr__(self) -> str:
        return f"Project(title={self._title!r}, owner={self.owner_name!r})"
