# Project Management CLI

A Python command-line tool for managing users, projects, and tasks. Data is stored locally as JSON files.

## Features

- Create, list, and delete **users**
- Create, list, update, and delete **projects** (scoped to users)
- Create, list, update, complete, and delete **tasks** (scoped to projects)
- Rich, colour-coded terminal output with progress bars
- Full JSON persistence across sessions
- Cascading deletes (removing a user removes their projects and tasks)

---

## Setup

### 1. Clone the repo

```bash
git clone <https://github.com/gabrielngige/Python-Project-Management-CLI-Tool-.git>
cd Project-management-CLI
```

### 2. Install dependencies

**With pip:**
```bash
pip install -r requirements.txt
```

**With Pipenv:**
```bash
pipenv install
pipenv shell
```

Python 3.10+ is required.

---

## Running the CLI

```bash
python main.py <command> [options]
```

Run `python main.py --help` for a full command list, or `python main.py <command> --help` for per-command help.

---

## Command Reference

### Users

| Command | Description |
|---|---|
| `add-user --name NAME --email EMAIL` | Create a new user |
| `list-users` | Display all users |
| `delete-user --name NAME` | Delete user and all their data |

### Projects

| Command | Description |
|---|---|
| `add-project --user NAME --title TITLE [--description DESC] [--due-date YYYY-MM-DD]` | Create a project |
| `list-projects [--user NAME]` | List all or one user's projects |
| `update-project --title TITLE [--new-title T] [--description D] [--due-date D]` | Edit a project |
| `project-detail --title TITLE` | Show project with full task list |
| `delete-project --title TITLE` | Delete project and its tasks |

### Tasks

| Command | Description |
|---|---|
| `add-task --project TITLE --title TITLE [--assigned-to NAME] [--status STATUS]` | Add a task |
| `list-tasks --project TITLE` | List tasks in a project |
| `complete-task --project TITLE --task TITLE` | Mark a task as done |
| `update-task --project TITLE --task TITLE [--new-title T] [--status S] [--assigned-to N]` | Update a task |
| `delete-task --project TITLE --task TITLE` | Remove a task |

Valid statuses: `todo`, `in-progress`, `done`

---

## Examples

```bash
# Set up users
python main.py add-user --name "Alice" --email "alice@dev.io"
python main.py add-user --name "Bob" --email "bob@dev.io"

# Create a project
python main.py add-project --user "Alice" --title "CLI Tool" \
    --description "Build a project tracker" --due-date 2026-12-31

# Add tasks
python main.py add-task --project "CLI Tool" --title "Setup repo" --assigned-to "Alice"
python main.py add-task --project "CLI Tool" --title "Write tests" --assigned-to "Bob"
python main.py add-task --project "CLI Tool" --title "Add README"

# Update and complete
python main.py update-task --project "CLI Tool" --task "Setup repo" --status in-progress
python main.py complete-task --project "CLI Tool" --task "Setup repo"

# View
python main.py project-detail --title "CLI Tool"
python main.py list-projects --user "Alice"
```

---

## Running Tests

```bash
pytest tests/ -v
```

---

## Project Structure

```
Project-management-CLI/
├── main.py          — CLI entry point and command handlers
├── models/
│   ├── person.py    — Base Person class
│   ├── user.py      — User (inherits Person)
│   ├── project.py   — Project (owns tasks)
│   └── task.py      — Task
├── utils/
│   ├── file_io.py   — JSON load/save helpers
│   ├── display.py   — Rich-powered terminal output
│   └── validators.py — Input validation
├── data/            — Auto-created JSON storage
├── tests/
│   ├── test_models.py
│   ├── test_cli.py
│   └── test_validators.py
├── requirements.txt
└── Pipfile
```

---

## Known Issues

- Project and user titles/names are used as lookup keys — renaming via `update-project --new-title` works correctly but any bookmarked names in your shell history will need updating.
- `delete-user` is irreversible; there is no undo. Always confirm before running.

---

## License

MIT
