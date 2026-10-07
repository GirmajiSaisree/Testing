"""Gherkin-derived tests for user login."""

import pytest
from playwright.sync_api import expect


@pytest.mark.functional
@pytest.mark.parametrize("test_case", ["LOGIN_TC_001"])
def test_login_with_valid_credentials(login_page, valid_username, valid_password, test_case):
    """LOGIN_TC_001: valid credentials authenticate and reach the dashboard."""
    assert test_case == "LOGIN_TC_001"
    login_page.submit_with_credentials(valid_username, valid_password)
    login_page.expect_logged_in()
    login_page.expect_dashboard()


@pytest.mark.api
def test_login_submits_backend_authentication_request(
    login_page, valid_username, valid_password
):
    """LOGIN_TC_002: submitting valid credentials calls the auth API."""
    login_page.enter_username(valid_username)
    login_page.enter_password(valid_password)
    response = login_page.wait_for_authentication_request()
    expect(response).to_be_ok()
    login_page.expect_logged_in()
    login_page.expect_dashboard()


@pytest.mark.negative
@pytest.mark.parametrize("invalid_field", ["username", "password"])
def test_login_rejects_invalid_credentials(
    login_page, valid_username, valid_password, invalid_field
):
    """LOGIN_TC_003: invalid username or password is rejected."""
    username = "invalid-user" if invalid_field == "username" else valid_username
    password = "invalid-password" if invalid_field == "password" else valid_password
    login_page.submit_with_credentials(username, password)
    login_page.expect_not_logged_in()
    login_page.expect_login_error()


@pytest.mark.validation
@pytest.mark.parametrize("empty_field", ["username", "password"])
def test_login_validates_mandatory_fields(
    login_page, valid_username, valid_password, empty_field
):
    """LOGIN_TC_004: an empty mandatory field displays validation feedback."""
    username = "" if empty_field == "username" else valid_username
    password = "" if empty_field == "password" else valid_password
    login_page.submit_with_credentials(username, password)
    login_page.expect_not_logged_in()
    login_page.expect_validation_for(empty_field)


@pytest.mark.functional
def test_password_is_masked(login_page):
    """LOGIN_TC_005: entered password is rendered as a masked value."""
    login_page.enter_password("example-password")
    login_page.expect_password_masked()


@pytest.mark.functional
def test_authenticated_user_remains_on_dashboard_after_refresh(
    login_page, valid_username, valid_password
):
    """LOGIN_TC_006: an authenticated dashboard session survives refresh."""
    login_page.submit_with_credentials(valid_username, valid_password)
    login_page.expect_dashboard()
    login_page.expect_authenticated_after_refresh()
