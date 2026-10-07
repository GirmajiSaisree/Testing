import os
from urllib.parse import urljoin

import pytest


pytestmark = pytest.mark.functional

USERNAME = os.getenv("LOGIN_USERNAME_SELECTOR", '[name="username"]')
PASSWORD = os.getenv("LOGIN_PASSWORD_SELECTOR", '[name="password"]')
SUBMIT = os.getenv("LOGIN_SUBMIT_SELECTOR", 'button[type="submit"]')
ERROR = os.getenv("LOGIN_ERROR_SELECTOR", '[role="alert"]')
DASHBOARD_PATH = os.getenv("LOGIN_DASHBOARD_PATH", "/dashboard")


def submit_login(page, username, password):
    page.locator(USERNAME).fill(username)
    page.locator(PASSWORD).fill(password)
    page.locator(SUBMIT).click()


def assert_dashboard(page):
    page.wait_for_url(f"**{DASHBOARD_PATH}")
    expected = urljoin(page.url, DASHBOARD_PATH)
    assert page.url.rstrip("/") == expected.rstrip("/")


def required_field_is_invalid(page, selector):
    field = page.locator(selector)
    return field.get_attribute("aria-invalid") == "true" or bool(
        field.evaluate("element => element.validationMessage")
    )


@pytest.fixture(scope="session")
def valid_username():
    value = os.getenv("LOGIN_VALID_USERNAME")
    if not value:
        pytest.fail("LOGIN_VALID_USERNAME is required")
    return value


@pytest.fixture(scope="session")
def valid_password():
    value = os.getenv("LOGIN_VALID_PASSWORD")
    if not value:
        pytest.fail("LOGIN_VALID_PASSWORD is required")
    return value


@pytest.fixture(scope="session")
def invalid_username():
    return os.getenv("LOGIN_INVALID_USERNAME", "invalid-user@example.test")


@pytest.fixture(scope="session")
def invalid_password():
    return os.getenv("LOGIN_INVALID_PASSWORD", "definitely-not-a-valid-password")


@pytest.mark.api
def test_LOGIN_TC_001_login_succeeds_with_valid_credentials(
    login_page, valid_username, valid_password
):
    submit_login(login_page, valid_username, valid_password)
    assert_dashboard(login_page)


@pytest.mark.api
@pytest.mark.negative
@pytest.mark.parametrize("credential_type", ["username", "password"])
def test_LOGIN_TC_002_invalid_credentials_are_rejected(
    login_page, valid_username, valid_password, invalid_username, invalid_password, credential_type
):
    username = invalid_username if credential_type == "username" else valid_username
    password = invalid_password if credential_type == "password" else valid_password
    submit_login(login_page, username, password)
    assert login_page.url.rstrip("/") != urljoin(login_page.url, DASHBOARD_PATH).rstrip("/")
    assert login_page.locator(ERROR).is_visible()
    assert login_page.locator(ERROR).inner_text().strip()


@pytest.mark.validation
@pytest.mark.negative
def test_LOGIN_TC_003_empty_username_shows_validation_message(login_page, valid_password):
    login_page.locator(PASSWORD).fill(valid_password)
    login_page.locator(SUBMIT).click()
    assert required_field_is_invalid(login_page, USERNAME)


@pytest.mark.validation
@pytest.mark.negative
def test_LOGIN_TC_004_empty_password_shows_validation_message(login_page, valid_username):
    login_page.locator(USERNAME).fill(valid_username)
    login_page.locator(SUBMIT).click()
    assert required_field_is_invalid(login_page, PASSWORD)


@pytest.mark.security
def test_LOGIN_TC_005_password_is_masked(login_page):
    password = login_page.locator(PASSWORD)
    assert password.get_attribute("type") == "password"
    password.fill("not-a-real-password")
    assert password.get_attribute("type") == "password"


@pytest.mark.security
def test_LOGIN_TC_006_dashboard_session_survives_refresh(login_page, valid_username, valid_password):
    submit_login(login_page, valid_username, valid_password)
    assert_dashboard(login_page)
    dashboard_url = login_page.url
    login_page.reload(wait_until="networkidle")
    assert login_page.url == dashboard_url
