"""Unit tests for Person, User, Task, and Project models."""

import pytest
from models.person import Person
from models.user import User
from models.project import Project
from models.task import Task, VALID_STATUSES


# ── Person ─────────────────────────────────────────────────────────────────────

class TestPerson:
    def test_stores_name_and_email(self):
        p = Person("Alice", "alice@example.com")
        assert p.name == "Alice"
        assert p.email == "alice@example.com"

    def test_email_is_lowercased(self):
        p = Person("Alice", "Alice@Example.COM")
        assert p.email == "alice@example.com"

    def test_empty_name_raises(self):
        with pytest.raises(ValueError, match="Name"):
            Person("", "a@b.com")

    def test_whitespace_name_raises(self):
        with pytest.raises(ValueError):
            Person("   ", "a@b.com")

    def test_invalid_email_raises(self):
        with pytest.raises(ValueError, match="Invalid email"):
            Person("X", "notanemail")

    def test_name_setter_strips_whitespace(self):
        p = Person("  Bob  ", "b@b.com")
        assert p.name == "Bob"

    def test_repr(self):
        p = Person("Alice", "alice@example.com")
        assert "Alice" in repr(p)


# ── User ───────────────────────────────────────────────────────────────────────

class TestUser:
    def setup_method(self):
        User._all.clear()
        User._id_counter = 1

    def test_inherits_person(self):
        u = User("Alice", "alice@example.com")
        assert isinstance(u, Person)

    def test_auto_increments_id(self):
        u1 = User("Alice", "a@a.com")
        u2 = User("Bob", "b@b.com")
        assert u1.id == 1
        assert u2.id == 2

    def test_add_project(self):
        u = User("Alice", "a@a.com")
        p = Project("My Project", owner_name="Alice")
        u.add_project(p)
        assert len(u.projects) == 1
        assert u.projects[0] is p

    def test_remove_project(self):
        u = User("Alice", "a@a.com")
        p = Project("My Project", owner_name="Alice")
        u.add_project(p)
        u.remove_project(p)
        assert len(u.projects) == 0

    def test_projects_returns_copy(self):
        u = User("Alice", "a@a.com")
        u.add_project(Project("P1"))
        lst = u.projects
        lst.clear()
        assert len(u.projects) == 1  # original unaffected

    def test_find_by_name_case_insensitive(self):
        u = User("Alice", "a@a.com")
        User._all.append(u)
        assert User.find_by_name("alice") is u
        assert User.find_by_name("ALICE") is u

    def test_find_by_name_missing(self):
        assert User.find_by_name("ghost") is None

    def test_to_dict(self):
        u = User("Alice", "alice@example.com")
        d = u.to_dict()
        assert d == {"id": 1, "name": "Alice", "email": "alice@example.com"}

    def test_from_dict_roundtrip(self):
        original = User("Bob", "bob@test.com")
        u = User.from_dict(original.to_dict())
        assert u.name == "Bob"
        assert u.email == "bob@test.com"

    def test_str_representation(self):
        u = User("Alice", "a@a.com")
        assert "Alice" in str(u)


# ── Task ───────────────────────────────────────────────────────────────────────

class TestTask:
    def setup_method(self):
        Task._id_counter = 1

    def test_default_status_is_todo(self):
        t = Task("Write tests")
        assert t.status == "todo"

    def test_complete_sets_done(self):
        t = Task("Write tests")
        t.complete()
        assert t.status == "done"

    def test_all_valid_statuses_accepted(self):
        t = Task("X")
        for s in VALID_STATUSES:
            t.status = s
            assert t.status == s

    def test_invalid_status_raises(self):
        with pytest.raises(ValueError, match="Status"):
            t = Task("X")
            t.status = "pending"

    def test_empty_title_raises(self):
        with pytest.raises(ValueError):
            Task("")

    def test_title_setter_strips_whitespace(self):
        t = Task("  Deploy  ")
        assert t.title == "Deploy"

    def test_assigned_to_stored(self):
        t = Task("Deploy", assigned_to="Alice")
        assert t.assigned_to == "Alice"

    def test_to_dict(self):
        t = Task("Deploy", "in-progress", "Alice")
        d = t.to_dict()
        assert d["title"] == "Deploy"
        assert d["status"] == "in-progress"
        assert d["assigned_to"] == "Alice"

    def test_from_dict_roundtrip(self):
        t = Task.from_dict({"id": 5, "title": "Fix bug", "status": "done", "assigned_to": "Bob"})
        assert t.title == "Fix bug"
        assert t.status == "done"
        assert t.id == 5

    def test_str_shows_status_and_title(self):
        t = Task("Setup", "in-progress", "Alice")
        s = str(t)
        assert "in-progress" in s
        assert "Setup" in s
        assert "Alice" in s


# ── Project ────────────────────────────────────────────────────────────────────

class TestProject:
    def setup_method(self):
        Project._id_counter = 1
        Task._id_counter = 1

    def test_stores_all_fields(self):
        p = Project("CLI Tool", "Build a CLI", "2026-12-31", "Alice")
        assert p.title == "CLI Tool"
        assert p.description == "Build a CLI"
        assert p.due_date == "2026-12-31"
        assert p.owner_name == "Alice"

    def test_invalid_due_date_raises(self):
        with pytest.raises(ValueError):
            p = Project("X")
            p.due_date = "31-12-2026"

    def test_empty_title_raises(self):
        with pytest.raises(ValueError):
            Project("")

    def test_add_and_find_task(self):
        p = Project("P")
        t = Task("Implement")
        p.add_task(t)
        assert p.find_task("implement") is t  # case-insensitive

    def test_remove_task(self):
        p = Project("P")
        t = Task("Implement")
        p.add_task(t)
        p.remove_task(t)
        assert p.find_task("Implement") is None

    def test_tasks_returns_copy(self):
        p = Project("P")
        p.add_task(Task("A"))
        lst = p.tasks
        lst.clear()
        assert len(p.tasks) == 1

    def test_completion_rate_no_tasks(self):
        assert Project("P").completion_rate() == 0.0

    def test_completion_rate_half(self):
        p = Project("P")
        p.add_task(Task("A", "done"))
        p.add_task(Task("B", "todo"))
        assert p.completion_rate() == 0.5

    def test_completion_rate_all_done(self):
        p = Project("P")
        p.add_task(Task("A", "done"))
        p.add_task(Task("B", "done"))
        assert p.completion_rate() == 1.0

    def test_to_dict_includes_tasks(self):
        p = Project("P", owner_name="Alice")
        p.add_task(Task("A"))
        d = p.to_dict()
        assert d["title"] == "P"
        assert len(d["tasks"]) == 1

    def test_from_dict_roundtrip(self):
        p = Project("Roundtrip", "desc", "2026-01-01", "Alice")
        p.add_task(Task("A task", "todo", "Alice"))
        d = p.to_dict()
        p2 = Project.from_dict(d)
        assert p2.title == "Roundtrip"
        assert len(p2.tasks) == 1
        assert p2.tasks[0].title == "A task"
