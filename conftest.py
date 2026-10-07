import os

import pytest

try:
    from playwright.sync_api import sync_playwright
except ImportError:  # pragma: no cover
    sync_playwright = None


@pytest.fixture(scope="session")
def app_url():
    return os.getenv("LOGIN_APP_URL", "").rstrip("/")


@pytest.fixture(scope="session")
def browser_context_args():
    return {
        "ignore_https_errors": os.getenv("LOGIN_IGNORE_HTTPS_ERRORS", "false").lower() == "true"
    }


@pytest.fixture(scope="session")
def browser(browser_context_args):
    if sync_playwright is None:
        pytest.fail("Install the playwright package before running login tests")
    with sync_playwright() as playwright:
        browser_name = os.getenv("LOGIN_BROWSER", "chromium")
        browser_type = getattr(playwright, browser_name)
        launched = browser_type.launch(
            headless=os.getenv("LOGIN_HEADLESS", "true").lower() == "true"
        )
        yield launched
        launched.close()


@pytest.fixture
def page(browser, browser_context_args):
    context = browser.new_context(**browser_context_args)
    page = context.new_page()
    yield page
    context.close()


@pytest.fixture
def login_page(page, app_url):
    if not app_url:
        pytest.fail("LOGIN_APP_URL must identify the application login page")
    page.goto(app_url, wait_until="networkidle")
    return page
