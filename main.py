#!/usr/bin/env python3
"""CLI entry point — argument parsing and command dispatch."""

import argparse
import sys

from utils.file_io import load_all, save_all
from utils.display import (
    success, error, info,
    print_users_table, print_projects_table,
    print_project_detail, print_tasks_table,
)
from utils import validators
from models.user import User
from models.project import Project
from models.task import Task


# ── Parser ─────────────────────────────────────────────────────────────────────

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="main.py",
        description="Project Management CLI — manage users, projects, and tasks.",
    )
    sub = parser.add_subparsers(dest="command", metavar="COMMAND")

    # ── user commands ──────────────────────────────────────────────────────────
    p = sub.add_parser("add-user", help="Create a new user")
    p.add_argument("--name", required=True, help="Full name")
    p.add_argument("--email", required=True, help="Email address")

    sub.add_parser("list-users", help="Display all users")

    p = sub.add_parser("delete-user", help="Delete a user and all their data")
    p.add_argument("--name", required=True)

    # ── project commands ───────────────────────────────────────────────────────
    p = sub.add_parser("add-project", help="Create a project for a user")
    p.add_argument("--user", required=True, help="Owner's name")
    p.add_argument("--title", required=True)
    p.add_argument("--description", default="")
    p.add_argument("--due-date", dest="due_date", default=None, metavar="YYYY-MM-DD")

    p = sub.add_parser("list-projects", help="List projects (all or per user)")
    p.add_argument("--user", default=None)

    p = sub.add_parser("update-project", help="Edit a project's fields")
    p.add_argument("--title", required=True, help="Current project title")
    p.add_argument("--new-title", dest="new_title", default=None)
    p.add_argument("--description", default=None)
    p.add_argument("--due-date", dest="due_date", default=None, metavar="YYYY-MM-DD")

    p = sub.add_parser("project-detail", help="Show project with full task list")
    p.add_argument("--title", required=True)

    p = sub.add_parser("delete-project", help="Delete a project and its tasks")
    p.add_argument("--title", required=True)

    # ── task commands ──────────────────────────────────────────────────────────
    p = sub.add_parser("add-task", help="Add a task to a project")
    p.add_argument("--project", required=True)
    p.add_argument("--title", required=True)
    p.add_argument("--assigned-to", dest="assigned_to", default=None)
    p.add_argument(
        "--status", default="todo",
        choices=["todo", "in-progress", "done"],
    )

    p = sub.add_parser("list-tasks", help="List tasks in a project")
    p.add_argument("--project", required=True)

    p = sub.add_parser("complete-task", help="Mark a task as done")
    p.add_argument("--project", required=True)
    p.add_argument("--task", required=True)

    p = sub.add_parser("update-task", help="Update a task's fields")
    p.add_argument("--project", required=True)
    p.add_argument("--task", required=True)
    p.add_argument("--new-title", dest="new_title", default=None)
    p.add_argument(
        "--status", default=None,
        choices=["todo", "in-progress", "done"],
    )
    p.add_argument("--assigned-to", dest="assigned_to", default=None)

    p = sub.add_parser("delete-task", help="Remove a task from a project")
    p.add_argument("--project", required=True)
    p.add_argument("--task", required=True)

    return parser


# ── Shared lookup ──────────────────────────────────────────────────────────────

def _find_project(title: str):
    """Search all users' projects for a case-insensitive title match."""
    for user in User.all():
        for project in user.projects:
            if project.title.lower() == title.lower():
                return project
    return None


# ── User handlers ──────────────────────────────────────────────────────────────

def cmd_add_user(args) -> None:
    """Create and persist a new User."""
    try:
        name = validators.validate_name(args.name)
        email = validators.validate_email(args.email)
    except ValueError as exc:
        error(str(exc))
        return

    if User.find_by_name(name):
        error(f"User '{name}' already exists.")
        return

    user = User(name, email)
    User._all.append(user)
    save_all()
    success(f"User '{user.name}' created (id={user.id}).")


def cmd_list_users(args) -> None:
    print_users_table(User.all())


def cmd_delete_user(args) -> None:
    """Remove user and cascade-delete all their projects/tasks."""
    user = User.find_by_name(args.name)
    if not user:
        error(f"User '{args.name}' not found.")
        return
    User._all.remove(user)
    save_all()
    success(f"User '{user.name}' and all their projects/tasks deleted.")


# ── Project handlers ────────────────────────────────────────────────────────────

def cmd_add_project(args) -> None:
    """Create a new Project under the given user."""
    user = User.find_by_name(args.user)
    if not user:
        error(f"User '{args.user}' not found.")
        return
    try:
        title = validators.validate_name(args.title)
        due_date = validators.validate_date(args.due_date)
    except ValueError as exc:
        error(str(exc))
        return

    if _find_project(title):
        error(f"Project '{title}' already exists.")
        return

    project = Project(title, args.description or "", due_date, user.name)
    user.add_project(project)
    save_all()
    success(f"Project '{project.title}' added to user '{user.name}'.")


def cmd_list_projects(args) -> None:
    if args.user:
        user = User.find_by_name(args.user)
        if not user:
            error(f"User '{args.user}' not found.")
            return
        print_projects_table(user.projects)
    else:
        all_projects = [p for u in User.all() for p in u.projects]
        print_projects_table(all_projects)


def cmd_update_project(args) -> None:
    project = _find_project(args.title)
    if not project:
        error(f"Project '{args.title}' not found.")
        return
    try:
        if args.new_title:
            project.title = validators.validate_name(args.new_title)
        if args.description is not None:
            project.description = args.description
        if args.due_date is not None:
            project.due_date = validators.validate_date(args.due_date)
    except ValueError as exc:
        error(str(exc))
        return
    save_all()
    success("Project updated.")


def cmd_project_detail(args) -> None:
    project = _find_project(args.title)
    if not project:
        error(f"Project '{args.title}' not found.")
        return
    print_project_detail(project)


def cmd_delete_project(args) -> None:
    for user in User.all():
        for project in user.projects:
            if project.title.lower() == args.title.lower():
                user.remove_project(project)
                save_all()
                success(f"Project '{project.title}' deleted.")
                return
    error(f"Project '{args.title}' not found.")


# ── Task handlers ──────────────────────────────────────────────────────────────

def cmd_add_task(args) -> None:
    project = _find_project(args.project)
    if not project:
        error(f"Project '{args.project}' not found.")
        return
    try:
        title = validators.validate_name(args.title)
    except ValueError as exc:
        error(str(exc))
        return

    if project.find_task(title):
        error(f"Task '{title}' already exists in project '{project.title}'.")
        return

    task = Task(title, args.status, args.assigned_to)
    project.add_task(task)
    save_all()
    success(f"Task '{task.title}' added to project '{project.title}'.")


def cmd_list_tasks(args) -> None:
    project = _find_project(args.project)
    if not project:
        error(f"Project '{args.project}' not found.")
        return
    print_tasks_table(project.tasks)


def cmd_complete_task(args) -> None:
    project = _find_project(args.project)
    if not project:
        error(f"Project '{args.project}' not found.")
        return
    task = project.find_task(args.task)
    if not task:
        error(f"Task '{args.task}' not found in project '{project.title}'.")
        return
    task.complete()
    save_all()
    success(f"Task '{task.title}' marked as done.")


def cmd_update_task(args) -> None:
    project = _find_project(args.project)
    if not project:
        error(f"Project '{args.project}' not found.")
        return
    task = project.find_task(args.task)
    if not task:
        error(f"Task '{args.task}' not found in project '{project.title}'.")
        return
    try:
        if args.new_title:
            task.title = validators.validate_name(args.new_title)
        if args.status:
            task.status = args.status
        if args.assigned_to is not None:
            task.assigned_to = args.assigned_to
    except ValueError as exc:
        error(str(exc))
        return
    save_all()
    success("Task updated.")


def cmd_delete_task(args) -> None:
    project = _find_project(args.project)
    if not project:
        error(f"Project '{args.project}' not found.")
        return
    task = project.find_task(args.task)
    if not task:
        error(f"Task '{args.task}' not found in project '{project.title}'.")
        return
    project.remove_task(task)
    save_all()
    success(f"Task '{task.title}' deleted.")


# ── Dispatch table ─────────────────────────────────────────────────────────────

HANDLERS = {
    "add-user":       cmd_add_user,
    "list-users":     cmd_list_users,
    "delete-user":    cmd_delete_user,
    "add-project":    cmd_add_project,
    "list-projects":  cmd_list_projects,
    "update-project": cmd_update_project,
    "project-detail": cmd_project_detail,
    "delete-project": cmd_delete_project,
    "add-task":       cmd_add_task,
    "list-tasks":     cmd_list_tasks,
    "complete-task":  cmd_complete_task,
    "update-task":    cmd_update_task,
    "delete-task":    cmd_delete_task,
}


if __name__ == "__main__":
    load_all()
    parser = build_parser()
    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        sys.exit(0)
    handler = HANDLERS.get(args.command)
    if handler:
        handler(args)
    else:
        error(f"Unknown command: {args.command}")
        sys.exit(1)
