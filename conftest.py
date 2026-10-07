"""Shared fixtures for user-login UI and API tests."""

import os
from collections.abc import Generator

import pytest
import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options


@pytest.fixture(scope="session")
def base_url() -> str:
    return os.getenv("LOGIN_BASE_URL", "http://localhost:3000").rstrip("/")


@pytest.fixture(scope="session")
def auth_api_url(base_url: str) -> str:
    return os.getenv("AUTH_API_URL", f"{base_url}/api/auth/login")


@pytest.fixture(scope="session")
def valid_username() -> str:
    value = os.getenv("LOGIN_VALID_USERNAME")
    if not value:
        pytest.skip("Set LOGIN_VALID_USERNAME to run authenticated login scenarios")
    return value


@pytest.fixture(scope="session")
def valid_password() -> str:
    value = os.getenv("LOGIN_VALID_PASSWORD")
    if not value:
        pytest.skip("Set LOGIN_VALID_PASSWORD to run authenticated login scenarios")
    return value


@pytest.fixture
def browser() -> Generator[webdriver.Chrome, None, None]:
    options = Options()
    if os.getenv("HEADLESS", "true").lower() not in {"0", "false", "no"}:
        options.add_argument("--headless=new")
    options.add_argument("--window-size=1440,1000")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    driver = webdriver.Chrome(options=options)
    driver.implicitly_wait(float(os.getenv("SELENIUM_IMPLICIT_WAIT", "2")))
    yield driver
    driver.quit()


@pytest.fixture
def login_page(browser: webdriver.Chrome, base_url: str):
    from pages.login_page import LoginPage

    page = LoginPage(browser, base_url)
    page.open()
    return page


@pytest.fixture
def auth_session() -> requests.Session:
    with requests.Session() as session:
        yield session
