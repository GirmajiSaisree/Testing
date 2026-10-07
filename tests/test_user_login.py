"""Acceptance coverage for Feature: User Login."""

import os

import pytest
import requests
from selenium.webdriver.common.by import By


@pytest.mark.functional
@pytest.mark.api
@pytest.mark.parametrize("username,password", [("valid", "valid")])
def test_LOGIN_TC_001_successful_login(login_page, valid_username, valid_password, auth_api_url, auth_session, username, password):
    """AC1: valid credentials are accepted by the API and UI redirects to dashboard."""
    response = auth_session.post(auth_api_url, json={"username": valid_username, "password": valid_password}, timeout=10)
    assert response.ok, f"Authentication API rejected valid credentials: {response.status_code}"
    login_page.submit_credentials(valid_username, valid_password)
    assert login_page.is_on_dashboard()


@pytest.mark.functional
@pytest.mark.negative
@pytest.mark.api
@pytest.mark.parametrize(
    ("username", "password"),
    [
        ("invalid_username", "ValidPassword123"),
        ("valid_username", "invalid_password"),
    ],
)
def test_LOGIN_TC_002_invalid_credentials(login_page, auth_api_url, auth_session, username, password):
    response = auth_session.post(auth_api_url, json={"username": username, "password": password}, timeout=10)
    assert response.status_code in {400, 401, 403}
    login_page.submit_credentials(username, password)
    assert login_page.is_on_login_page()
    assert login_page.has_error()


@pytest.mark.negative
@pytest.mark.validation
def test_LOGIN_TC_003_empty_credentials(login_page):
    login_page.submit()
    assert login_page.is_on_login_page()
    assert login_page.has_username_required_error()
    assert login_page.has_password_required_error()


@pytest.mark.negative
@pytest.mark.validation
def test_LOGIN_TC_004_empty_username(login_page, valid_password):
    login_page.enter_password(valid_password)
    login_page.submit()
    assert login_page.is_on_login_page()
    assert login_page.has_username_required_error()


@pytest.mark.negative
@pytest.mark.validation
def test_LOGIN_TC_005_empty_password(login_page, valid_username):
    login_page.enter_username(valid_username)
    login_page.submit()
    assert login_page.is_on_login_page()
    assert login_page.has_password_required_error()


@pytest.mark.functional
@pytest.mark.security
def test_LOGIN_TC_006_password_is_masked(login_page):
    secret = "NotDisplayedInPlainText123!"
    login_page.enter_password(secret)
    assert login_page.password_input_type() == "password"
    assert login_page.password_value() == secret
    assert login_page.driver.find_element(By.CSS_SELECTOR, 'input[type="password"]')


@pytest.mark.functional
@pytest.mark.security
def test_LOGIN_TC_007_session_survives_dashboard_refresh(login_page, valid_username, valid_password):
    login_page.submit_credentials(valid_username, valid_password)
    assert login_page.is_on_dashboard()
    login_page.driver.refresh()
    assert login_page.is_on_dashboard()
    assert login_page.driver.current_url.startswith(login_page.base_url)
