import pytest
from jwbuddy.data.security import validate_readonly


def test_validate_select():
    assert validate_readonly("SELECT * FROM users")


def test_validate_forbids_insert():
    assert not validate_readonly("INSERT INTO users VALUES (1)")


def test_validate_forbids_delete():
    assert not validate_readonly("DELETE FROM users WHERE id=1")


def test_validate_forbids_drop():
    assert not validate_readonly("DROP TABLE users")


def test_validate_ignores_strings():
    assert validate_readonly("SELECT * FROM users WHERE name = 'DROP TABLE'")
