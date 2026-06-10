"""Task model — a single unit of work inside a Project."""

from __future__ import annotations

VALID_STATUSES = ("todo", "in-progress", "done")


class Task:
    """Represents one task.  Status flows: todo → in-progress → done."""

    _id_counter: int = 1

    def __init__(
        self,
        title: str,
        status: str = "todo",
        assigned_to: str | None = None,
    ) -> None:
        self.id = Task._id_counter
        Task._id_counter += 1
        self.title = title          # uses setter
        self.status = status        # uses setter
        self._assigned_to = assigned_to

    # ── title ──────────────────────────────────────────────────────────────────

    @property
    def title(self) -> str:
        return self._title

    @title.setter
    def title(self, value: str) -> None:
        if not value or not value.strip():
            raise ValueError("Task title cannot be empty.")
        self._title = value.strip()

    # ── status ─────────────────────────────────────────────────────────────────

    @property
    def status(self) -> str:
        return self._status

    @status.setter
    def status(self, value: str) -> None:
        if value not in VALID_STATUSES:
            raise ValueError(
                f"Status must be one of: {', '.join(VALID_STATUSES)}"
            )
        self._status = value

    # ── assigned_to ────────────────────────────────────────────────────────────

    @property
    def assigned_to(self) -> str | None:
        return self._assigned_to

    @assigned_to.setter
    def assigned_to(self, value: str | None) -> None:
        self._assigned_to = value

    # ── behaviour ──────────────────────────────────────────────────────────────

    def complete(self) -> None:
        """Shortcut to mark the task done."""
        self._status = "done"

    # ── serialisation ──────────────────────────────────────────────────────────

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "title": self.title,
            "status": self.status,
            "assigned_to": self.assigned_to,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Task":
        task = cls(data["title"], data.get("status", "todo"), data.get("assigned_to"))
        task.id = data.get("id", task.id)
        return task

    def __str__(self) -> str:
        assignee = f" → {self._assigned_to}" if self._assigned_to else ""
        return f"[{self._status}] {self._title}{assignee}"

    def __repr__(self) -> str:
        return f"Task(title={self._title!r}, status={self._status!r})"
