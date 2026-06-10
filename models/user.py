"""User model — inherits Person and owns a list of Projects."""

from __future__ import annotations
from models.person import Person
from models.project import Project


class User(Person):
    """A named, authenticated user who owns one or more projects."""

    _id_counter: int = 1
    _all: list["User"] = []

    def __init__(self, name: str, email: str) -> None:
        super().__init__(name, email)
        self.id = User._id_counter
        User._id_counter += 1
        self._projects: list[Project] = []

    # ── project collection ─────────────────────────────────────────────────────

    @property
    def projects(self) -> list[Project]:
        return list(self._projects)

    def add_project(self, project: Project) -> None:
        self._projects.append(project)

    def remove_project(self, project: Project) -> None:
        self._projects.remove(project)

    # ── class-level registry ───────────────────────────────────────────────────

    @classmethod
    def all(cls) -> list["User"]:
        return list(cls._all)

    @classmethod
    def find_by_name(cls, name: str) -> "User | None":
        """Case-insensitive lookup."""
        return next(
            (u for u in cls._all if u.name.lower() == name.lower()), None
        )

    # ── serialisation ──────────────────────────────────────────────────────────

    def to_dict(self) -> dict:
        return {"id": self.id, "name": self.name, "email": self.email}

    @classmethod
    def from_dict(cls, data: dict) -> "User":
        user = cls(data["name"], data["email"])
        user.id = data.get("id", user.id)
        return user

    def __str__(self) -> str:
        return (
            f"User: {self.name} <{self.email}> "
            f"| Projects: {len(self._projects)}"
        )
