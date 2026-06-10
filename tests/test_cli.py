"""Integration tests for all CLI commands using isolated in-memory/file state."""

import os
import sys
import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import utils.file_io as file_io
from models.user import User
from models.project import Project
from models.task import Task


@pytest.fixture(autouse=True)
def reset_state(tmp_path):
    """Reset global state and redirect persistence to a temp directory."""
    User._all.clear()
    User._id_counter = 1
    Project._id_counter = 1
    Task._id_counter = 1

    file_io.DATA_DIR = str(tmp_path)
    file_io.USERS_FILE = str(tmp_path / "users.json")
    file_io.PROJECTS_FILE = str(tmp_path / "projects.json")

    yield

    User._all.clear()


def _run(args_list: list[str]) -> None:
    """Parse args and dispatch to the matching CLI handler."""
    from main import build_parser, HANDLERS
    parser = build_parser()
    args = parser.parse_args(args_list)
    handler = HANDLERS.get(args.command)
    if handler:
        handler(args)


# ── User commands ──────────────────────────────────────────────────────────────

class TestAddUser:
    def test_creates_user(self):
        _run(["add-user", "--name", "Alice", "--email", "alice@test.com"])
        assert User.find_by_name("Alice") is not None

    def test_rejects_duplicate_name(self):
        _run(["add-user", "--name", "Alice", "--email", "a1@test.com"])
        _run(["add-user", "--name", "Alice", "--email", "a2@test.com"])
        assert len(User.all()) == 1

    def test_rejects_invalid_email(self, capsys):
        _run(["add-user", "--name", "Alice", "--email", "bad-email"])
        captured = capsys.readouterr()
        assert "Invalid email" in captured.out
        assert User.find_by_name("Alice") is None

    def test_persists_to_file(self):
        _run(["add-user", "--name", "Alice", "--email", "alice@test.com"])
        User._all.clear()
        file_io.load_all()
        assert User.find_by_name("Alice") is not None


class TestListUsers:
    def test_shows_user_in_output(self, capsys):
        _run(["add-user", "--name", "Alice", "--email", "alice@test.com"])
        _run(["list-users"])
        assert "Alice" in capsys.readouterr().out

    def test_empty_shows_no_users_message(self, capsys):
        _run(["list-users"])
        assert "No users" in capsys.readouterr().out


class TestDeleteUser:
    def test_removes_user(self):
        _run(["add-user", "--name", "Alice", "--email", "alice@test.com"])
        _run(["delete-user", "--name", "Alice"])
        assert User.find_by_name("Alice") is None

    def test_cascades_to_projects(self):
        _run(["add-user", "--name", "Alice", "--email", "alice@test.com"])
        _run(["add-project", "--user", "Alice", "--title", "P1"])
        _run(["delete-user", "--name", "Alice"])
        User._all.clear()
        file_io.load_all()
        assert User.find_by_name("Alice") is None

    def test_unknown_user_prints_error(self, capsys):
        _run(["delete-user", "--name", "Ghost"])
        assert "not found" in capsys.readouterr().out


# ── Project commands ───────────────────────────────────────────────────────────

class TestAddProject:
    def test_creates_project(self):
        _run(["add-user", "--name", "Alice", "--email", "alice@test.com"])
        _run(["add-project", "--user", "Alice", "--title", "CLI Tool"])
        assert len(User.find_by_name("Alice").projects) == 1

    def test_stores_description_and_due_date(self):
        _run(["add-user", "--name", "Alice", "--email", "alice@test.com"])
        _run(["add-project", "--user", "Alice", "--title", "P1",
              "--description", "My desc", "--due-date", "2026-12-31"])
        p = User.find_by_name("Alice").projects[0]
        assert p.description == "My desc"
        assert p.due_date == "2026-12-31"

    def test_unknown_user_prints_error(self, capsys):
        _run(["add-project", "--user", "Ghost", "--title", "P"])
        assert "not found" in capsys.readouterr().out

    def test_rejects_duplicate_title(self, capsys):
        _run(["add-user", "--name", "Alice", "--email", "a@a.com"])
        _run(["add-project", "--user", "Alice", "--title", "Dup"])
        _run(["add-project", "--user", "Alice", "--title", "Dup"])
        assert len(User.find_by_name("Alice").projects) == 1

    def test_rejects_invalid_due_date(self, capsys):
        _run(["add-user", "--name", "Alice", "--email", "a@a.com"])
        _run(["add-project", "--user", "Alice", "--title", "P", "--due-date", "31-12-2026"])
        assert "YYYY-MM-DD" in capsys.readouterr().out


class TestUpdateProject:
    def test_renames_project(self):
        _run(["add-user", "--name", "Alice", "--email", "a@a.com"])
        _run(["add-project", "--user", "Alice", "--title", "Old"])
        _run(["update-project", "--title", "Old", "--new-title", "New"])
        assert User.find_by_name("Alice").projects[0].title == "New"

    def test_updates_description(self):
        _run(["add-user", "--name", "Alice", "--email", "a@a.com"])
        _run(["add-project", "--user", "Alice", "--title", "P"])
        _run(["update-project", "--title", "P", "--description", "Updated"])
        assert User.find_by_name("Alice").projects[0].description == "Updated"


class TestDeleteProject:
    def test_removes_project(self):
        _run(["add-user", "--name", "Alice", "--email", "a@a.com"])
        _run(["add-project", "--user", "Alice", "--title", "Temp"])
        _run(["delete-project", "--title", "Temp"])
        assert len(User.find_by_name("Alice").projects) == 0

    def test_unknown_project_prints_error(self, capsys):
        _run(["delete-project", "--title", "Ghost"])
        assert "not found" in capsys.readouterr().out


# ── Task commands ──────────────────────────────────────────────────────────────

class TestAddTask:
    def _setup(self):
        _run(["add-user", "--name", "Alice", "--email", "a@a.com"])
        _run(["add-project", "--user", "Alice", "--title", "P"])

    def test_creates_task(self):
        self._setup()
        _run(["add-task", "--project", "P", "--title", "Write tests"])
        assert User.find_by_name("Alice").projects[0].find_task("Write tests") is not None

    def test_sets_assigned_to(self):
        self._setup()
        _run(["add-task", "--project", "P", "--title", "T", "--assigned-to", "Bob"])
        task = User.find_by_name("Alice").projects[0].find_task("T")
        assert task.assigned_to == "Bob"

    def test_sets_initial_status(self):
        self._setup()
        _run(["add-task", "--project", "P", "--title", "T", "--status", "in-progress"])
        task = User.find_by_name("Alice").projects[0].find_task("T")
        assert task.status == "in-progress"

    def test_rejects_duplicate_task(self, capsys):
        self._setup()
        _run(["add-task", "--project", "P", "--title", "T"])
        _run(["add-task", "--project", "P", "--title", "T"])
        assert len(User.find_by_name("Alice").projects[0].tasks) == 1

    def test_unknown_project_prints_error(self, capsys):
        _run(["add-task", "--project", "Ghost", "--title", "T"])
        assert "not found" in capsys.readouterr().out


class TestCompleteTask:
    def _setup(self):
        _run(["add-user", "--name", "Alice", "--email", "a@a.com"])
        _run(["add-project", "--user", "Alice", "--title", "P"])
        _run(["add-task", "--project", "P", "--title", "T"])

    def test_marks_task_done(self):
        self._setup()
        _run(["complete-task", "--project", "P", "--task", "T"])
        task = User.find_by_name("Alice").projects[0].find_task("T")
        assert task.status == "done"


class TestUpdateTask:
    def _setup(self):
        _run(["add-user", "--name", "Alice", "--email", "a@a.com"])
        _run(["add-project", "--user", "Alice", "--title", "P"])
        _run(["add-task", "--project", "P", "--title", "T"])

    def test_changes_status(self):
        self._setup()
        _run(["update-task", "--project", "P", "--task", "T", "--status", "in-progress"])
        task = User.find_by_name("Alice").projects[0].find_task("T")
        assert task.status == "in-progress"

    def test_changes_assigned_to(self):
        self._setup()
        _run(["update-task", "--project", "P", "--task", "T", "--assigned-to", "Bob"])
        task = User.find_by_name("Alice").projects[0].find_task("T")
        assert task.assigned_to == "Bob"

    def test_renames_task(self):
        self._setup()
        _run(["update-task", "--project", "P", "--task", "T", "--new-title", "New T"])
        assert User.find_by_name("Alice").projects[0].find_task("New T") is not None


class TestDeleteTask:
    def test_removes_task(self):
        _run(["add-user", "--name", "Alice", "--email", "a@a.com"])
        _run(["add-project", "--user", "Alice", "--title", "P"])
        _run(["add-task", "--project", "P", "--title", "T"])
        _run(["delete-task", "--project", "P", "--task", "T"])
        assert User.find_by_name("Alice").projects[0].find_task("T") is None


# ── Persistence round-trip ─────────────────────────────────────────────────────

class TestPersistence:
    def test_full_roundtrip(self):
        _run(["add-user", "--name", "Alice", "--email", "alice@test.com"])
        _run(["add-project", "--user", "Alice", "--title", "CLI Tool"])
        _run(["add-task", "--project", "CLI Tool", "--title", "Write tests", "--assigned-to", "Alice"])
        _run(["complete-task", "--project", "CLI Tool", "--task", "Write tests"])

        # Simulate fresh process start
        User._all.clear()
        User._id_counter = 1
        Project._id_counter = 1
        Task._id_counter = 1
        file_io.load_all()

        alice = User.find_by_name("Alice")
        assert alice is not None
        assert len(alice.projects) == 1
        task = alice.projects[0].find_task("Write tests")
        assert task is not None
        assert task.status == "done"
        assert task.assigned_to == "Alice"
