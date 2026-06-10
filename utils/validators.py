"""Input validation helpers shared across the CLI layer."""

import re
from datetime import datetime


def validate_name(name: str) -> str:
    """Return stripped name or raise ValueError."""
    if not name or not name.strip():
        raise ValueError("Name cannot be empty.")
    return name.strip()


def validate_email(email: str) -> str:
    """Basic RFC-style email check; returns lowercased canonical form."""
    pattern = r"^[^@\s]+@[^@\s]+\.[^@\s]+$"
    if not email or not re.match(pattern, email.strip()):
        raise ValueError(f"Invalid email address: {email!r}")
    return email.strip().lower()


def validate_date(date_str: str | None) -> str | None:
    """Expect YYYY-MM-DD or None; returns unchanged string or None."""
    if not date_str:
        return None
    try:
        datetime.strptime(date_str, "%Y-%m-%d")
    except ValueError:
        raise ValueError(
            f"Date must be in YYYY-MM-DD format, got: {date_str!r}"
        )
    return date_str


def validate_status(status: str) -> str:
    """Validate task status value against the allowed set."""
    from models.task import VALID_STATUSES
    if status not in VALID_STATUSES:
        raise ValueError(
            f"Status must be one of: {', '.join(VALID_STATUSES)}"
        )
    return status
