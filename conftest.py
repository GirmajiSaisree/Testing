"""Shared fixtures for the login automation suite."""

import os

import pytest
from playwright.sync_api import Page


@pytest.fixture(scope="session")
def app_base_url() -> str:
    """Return the application URL supplied by the test environment."""
    return os.getenv("APP_BASE_URL", "http://localhost:3000").rstrip("/")


@pytest.fixture(scope="session")
def valid_username() -> str:
    """Return a non-secret test username supplied by the test environment."""
    return os.getenv("TEST_USERNAME", "test-user")


@pytest.fixture(scope="session")
def valid_password() -> str:
    """Return a non-secret test password supplied by the test environment."""
    return os.getenv("TEST_PASSWORD", "test-password")


@pytest.fixture
def login_page(page: Page, app_base_url: str):
    """Navigate to the login page and return its page object."""
    from pages.login_page import LoginPage

    login = LoginPage(page, app_base_url)
    login.open()
    return login
