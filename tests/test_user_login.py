import pytest
from playwright.sync_api import Page

from pages.login_page import LoginPage


pytestmark = pytest.mark.login


def test_login_successfully_with_valid_credentials(
    login_page: LoginPage, valid_credentials: tuple[str, str]
) -> None:
    username, password = valid_credentials
    login_page.open()
    login_page.login(username, password)
    login_page.expect_logged_in()
    login_page.expect_dashboard()


def test_login_submits_backend_authentication_request(
    login_page: LoginPage,
    valid_credentials: tuple[str, str],
    page: Page,
) -> None:
    username, password = valid_credentials
    login_page.open()
    with page.expect_request(
        lambda request: login_page.API_PATH in request.url
        and request.method == "POST"
    ) as request_info:
        login_page.login(username, password)
    assert request_info.value.method == "POST"
    login_page.expect_logged_in()
    login_page.expect_dashboard()


@pytest.mark.parametrize("credential_type", ["username", "password"])
def test_invalid_login_credentials_are_rejected(
    login_page: LoginPage,
    valid_credentials: tuple[str, str],
    credential_type: str,
) -> None:
    username, password = valid_credentials
    if credential_type == "username":
        username = "invalid-username"
    else:
        password = "invalid-password"
    login_page.open()
    login_page.login(username, password)
    login_page.expect_not_logged_in()
    login_page.expect_login_page()
    login_page.expect_error()


def test_empty_username_shows_validation(
    login_page: LoginPage, valid_credentials: tuple[str, str]
) -> None:
    _, password = valid_credentials
    login_page.open()
    login_page.enter_password(password)
    login_page.submit_form()
    login_page.expect_not_logged_in()
    login_page.expect_username_validation()


def test_empty_password_shows_validation(
    login_page: LoginPage, valid_credentials: tuple[str, str]
) -> None:
    username, _ = valid_credentials
    login_page.open()
    login_page.enter_username(username)
    login_page.submit_form()
    login_page.expect_not_logged_in()
    login_page.expect_password_validation()


def test_empty_username_and_password_show_validation(login_page: LoginPage) -> None:
    login_page.open()
    login_page.submit_form()
    login_page.expect_not_logged_in()
    login_page.expect_username_validation()
    login_page.expect_password_validation()


def test_password_is_masked_when_entered(
    login_page: LoginPage, valid_credentials: tuple[str, str]
) -> None:
    _, password = valid_credentials
    login_page.open()
    login_page.enter_password(password)
    login_page.expect_password_masked()
    login_page.expect_password_plain_text_not_visible(password)


def test_authentication_survives_dashboard_refresh(
    login_page: LoginPage, valid_credentials: tuple[str, str]
) -> None:
    username, password = valid_credentials
    login_page.open()
    login_page.login(username, password)
    login_page.expect_dashboard()
    login_page.refresh()
    login_page.expect_logged_in()
    login_page.expect_dashboard()
