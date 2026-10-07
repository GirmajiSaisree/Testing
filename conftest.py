import os

import pytest
from playwright.sync_api import Page

from pages.login_page import LoginPage


@pytest.fixture(scope="session")
def browser_context_args(browser_context_args: dict) -> dict:
    return {
        **browser_context_args,
        "base_url": os.getenv("BASE_URL", "http://localhost:3000"),
    }


@pytest.fixture
def login_page(page: Page) -> LoginPage:
    page.set_default_timeout(int(os.getenv("PLAYWRIGHT_TIMEOUT_MS", "10000")))
    return LoginPage(page)


@pytest.fixture
def valid_credentials() -> tuple[str, str]:
    username = os.getenv("LOGIN_USERNAME")
    password = os.getenv("LOGIN_PASSWORD")
    if not username or not password:
        pytest.skip("Set LOGIN_USERNAME and LOGIN_PASSWORD to run login tests")
    return username, password
