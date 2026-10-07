import os
from urllib.parse import urljoin

import pytest


pytestmark = pytest.mark.functional

USERNAME = os.getenv("LOGIN_USERNAME_SELECTOR", '[name="username"]')
PASSWORD = os.getenv("LOGIN_PASSWORD_SELECTOR", '[name="password"]')
SUBMIT = os.getenv("LOGIN_SUBMIT_SELECTOR", 'button[type="submit"]')
ERROR = os.getenv("LOGIN_ERROR_SELECTOR", '[role="alert"]')
DASHBOARD_PATH = os.getenv("LOGIN_DASHBOARD_PATH", "/dashboard")
AUTH_API_PATH = os.getenv("LOGIN_AUTH_API_PATH", "/api/auth/login")


def submit_login(page, username, password):
    page.locator(USERNAME).fill(username)
    page.locator(PASSWORD).fill(password)
    page.locator(SUBMIT).click()


def is_dashboard(page):
    expected = urljoin(page.url, DASHBOARD_PATH)
    return page.url.rstrip("/") == expected.rstrip("/")


def assert_dashboard(page):
    page.wait_for_url(f"**{DASHBOARD_PATH}")
    assert is_dashboard(page)


def assert_error_message(page):
    error = page.locator(ERROR)
    assert error.is_visible()
    assert error.inner_text().strip()


def field_has_validation_message(page, selector):
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


@pytest.mark.functional
def test_LOGIN_TC_001_login_succeeds_with_valid_credentials(
    login_page, valid_username, valid_password
):
    submit_login(login_page, valid_username, valid_password)
    assert_dashboard(login_page)


@pytest.mark.negative
@pytest.mark.parametrize("invalid_credential", ["username", "password"])
def test_LOGIN_TC_002_invalid_credentials_are_rejected(
    login_page,
    valid_username,
    valid_password,
    invalid_username,
    invalid_password,
    invalid_credential,
):
    username = invalid_username if invalid_credential == "username" else valid_username
    password = invalid_password if invalid_credential == "password" else valid_password
    submit_login(login_page, username, password)
    assert not is_dashboard(login_page)
    assert_error_message(login_page)


@pytest.mark.validation
@pytest.mark.negative
@pytest.mark.parametrize(
    ("username", "password", "empty_fields"),
    [("", "valid", [USERNAME]), ("valid", "", [PASSWORD]), ("", "", [USERNAME, PASSWORD])],
)
def test_LOGIN_TC_003_empty_mandatory_fields_show_validation_messages(
    login_page, valid_username, valid_password, username, password, empty_fields
):
    login_page.locator(USERNAME).fill(valid_username if username == "valid" else "")
    login_page.locator(PASSWORD).fill(valid_password if password == "valid" else "")
    login_page.locator(SUBMIT).click()

    assert not is_dashboard(login_page)
    for selector in empty_fields:
        assert field_has_validation_message(login_page, selector)


@pytest.mark.functional
def test_LOGIN_TC_004_password_is_masked_while_entering(login_page):
    password = login_page.locator(PASSWORD)
    password.fill("not-a-real-password")
    assert password.get_attribute("type") == "password"


@pytest.mark.api
def test_LOGIN_TC_005_valid_login_uses_authentication_api(
    login_page, valid_username, valid_password
):
    with login_page.expect_request(
        lambda request: AUTH_API_PATH in request.url and request.method.upper() == "POST"
    ) as api_request:
        submit_login(login_page, valid_username, valid_password)

    request = api_request.value
    assert request.post_data_json["username"] == valid_username
    assert request.post_data_json["password"] == valid_password
    assert request.response().ok
    assert_dashboard(login_page)


@pytest.mark.functional
def test_LOGIN_TC_006_dashboard_session_survives_refresh(
    login_page, valid_username, valid_password
):
    submit_login(login_page, valid_username, valid_password)
    assert_dashboard(login_page)
    dashboard_url = login_page.url
    login_page.reload(wait_until="networkidle")
    assert login_page.url == dashboard_url
    assert is_dashboard(login_page)
