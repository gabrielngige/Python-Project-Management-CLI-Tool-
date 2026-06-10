"""Unit tests for utils/validators.py."""

import pytest
from utils import validators


class TestValidateName:
    def test_strips_whitespace(self):
        assert validators.validate_name("  Alice  ") == "Alice"

    def test_empty_string_raises(self):
        with pytest.raises(ValueError, match="empty"):
            validators.validate_name("")

    def test_whitespace_only_raises(self):
        with pytest.raises(ValueError):
            validators.validate_name("   ")

    def test_none_raises(self):
        with pytest.raises((ValueError, AttributeError)):
            validators.validate_name(None)


class TestValidateEmail:
    def test_valid_email(self):
        assert validators.validate_email("Alice@Example.COM") == "alice@example.com"

    def test_lowercases_result(self):
        assert validators.validate_email("BOB@TEST.IO") == "bob@test.io"

    def test_no_at_sign_raises(self):
        with pytest.raises(ValueError, match="Invalid email"):
            validators.validate_email("notanemail")

    def test_no_domain_raises(self):
        with pytest.raises(ValueError):
            validators.validate_email("user@")

    def test_empty_raises(self):
        with pytest.raises(ValueError):
            validators.validate_email("")


class TestValidateDate:
    def test_valid_date_passthrough(self):
        assert validators.validate_date("2026-12-31") == "2026-12-31"

    def test_none_returns_none(self):
        assert validators.validate_date(None) is None

    def test_empty_string_returns_none(self):
        assert validators.validate_date("") is None

    def test_wrong_format_raises(self):
        with pytest.raises(ValueError, match="YYYY-MM-DD"):
            validators.validate_date("31-12-2026")

    def test_invalid_month_raises(self):
        with pytest.raises(ValueError):
            validators.validate_date("2026-13-01")


class TestValidateStatus:
    def test_todo(self):
        assert validators.validate_status("todo") == "todo"

    def test_in_progress(self):
        assert validators.validate_status("in-progress") == "in-progress"

    def test_done(self):
        assert validators.validate_status("done") == "done"

    def test_invalid_raises(self):
        with pytest.raises(ValueError, match="Status"):
            validators.validate_status("pending")

    def test_case_sensitive(self):
        with pytest.raises(ValueError):
            validators.validate_status("Todo")
