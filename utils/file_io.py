"""JSON persistence — load and save all application state."""

import json
import os

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
USERS_FILE = os.path.join(DATA_DIR, "users.json")
PROJECTS_FILE = os.path.join(DATA_DIR, "projects.json")


def _ensure_data_dir() -> None:
    os.makedirs(DATA_DIR, exist_ok=True)


def load_json(path: str) -> list:
    """Return parsed JSON list from path, or [] on missing / corrupt file."""
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return []
    except json.JSONDecodeError:
        return []


def save_json(path: str, data: list) -> None:
    _ensure_data_dir()
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def load_all() -> list:
    """Populate User._all from JSON files; returns the loaded user list."""
    from models.user import User
    from models.project import Project
    from models.task import Task

    User._all.clear()
    User._id_counter = 1
    Project._id_counter = 1
    Task._id_counter = 1

    users_data = load_json(USERS_FILE)
    projects_data = load_json(PROJECTS_FILE)

    for ud in users_data:
        u = User.from_dict(ud)
        User._all.append(u)
        if u.id >= User._id_counter:
            User._id_counter = u.id + 1

    for pd in projects_data:
        p = Project.from_dict(pd)
        if p.id >= Project._id_counter:
            Project._id_counter = p.id + 1
        for task in p.tasks:
            if task.id >= Task._id_counter:
                Task._id_counter = task.id + 1
        owner = User.find_by_name(p.owner_name or "")
        if owner:
            owner.add_project(p)

    return User.all()


def save_all() -> None:
    """Persist all users and their projects/tasks to JSON."""
    from models.user import User

    users = User.all()
    all_projects = [p for u in users for p in u.projects]

    save_json(USERS_FILE, [u.to_dict() for u in users])
    save_json(PROJECTS_FILE, [p.to_dict() for p in all_projects])
