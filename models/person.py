"""Base class representing a named person with an email address."""

import re


class Person:
    """Shared base for any entity that has a name and email."""

    def __init__(self, name: str, email: str) -> None:
        # Use setters so validation fires on construction too.
        self.name = name
        self.email = email

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, value: str) -> None:
        if not value or not value.strip():
            raise ValueError("Name cannot be empty.")
        self._name = value.strip()

    @property
    def email(self) -> str:
        return self._email

    @email.setter
    def email(self, value: str) -> None:
        pattern = r"^[^@\s]+@[^@\s]+\.[^@\s]+$"
        if not value or not re.match(pattern, value.strip()):
            raise ValueError(f"Invalid email address: {value!r}")
        self._email = value.strip().lower()

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(name={self._name!r}, email={self._email!r})"
