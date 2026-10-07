from __future__ import annotations

import os
from typing import Final

from playwright.sync_api import Page, expect


class LoginPage:
    LOGIN_PATH: Final[str] = os.getenv("LOGIN_PATH", "/login")
    DASHBOARD_PATH: Final[str] = os.getenv("DASHBOARD_PATH", "/dashboard")
    API_PATH: Final[str] = os.getenv("LOGIN_API_PATH", "/api/auth/login")

    def __init__(self, page: Page) -> None:
        self.page = page
        self.username = page.get_by_label(os.getenv("USERNAME_LABEL", "Username"))
        self.password = page.get_by_label(os.getenv("PASSWORD_LABEL", "Password"))
        self.submit = page.get_by_role(
            "button", name=os.getenv("SUBMIT_BUTTON_NAME", "Login")
        )
        self.error_message = page.locator(
            os.getenv("LOGIN_ERROR_SELECTOR", "[role='alert']")
        )
        self.authenticated_indicator = page.locator(
            os.getenv("AUTHENTICATED_SELECTOR", "[data-authenticated='true']")
        )

    def open(self) -> None:
        self.page.goto(self.LOGIN_PATH)

    def enter_username(self, value: str) -> None:
        self.username.fill(value)

    def enter_password(self, value: str) -> None:
        self.password.fill(value)

    def submit_form(self) -> None:
        self.submit.click()

    def login(self, username: str, password: str) -> None:
        self.enter_username(username)
        self.enter_password(password)
        self.submit_form()

    def expect_dashboard(self) -> None:
        expect(self.page).to_have_url(lambda url: self.DASHBOARD_PATH in url)

    def expect_login_page(self) -> None:
        expect(self.page).to_have_url(lambda url: self.LOGIN_PATH in url)

    def expect_logged_in(self) -> None:
        expect(self.authenticated_indicator).to_be_visible()

    def expect_not_logged_in(self) -> None:
        expect(self.authenticated_indicator).not_to_be_visible()

    def expect_error(self) -> None:
        expect(self.error_message).to_be_visible()

    def expect_username_validation(self) -> None:
        expect(self.username).to_have_attribute("aria-invalid", "true")

    def expect_password_validation(self) -> None:
        expect(self.password).to_have_attribute("aria-invalid", "true")

    def expect_password_masked(self) -> None:
        expect(self.password).to_have_attribute("type", "password")

    def expect_password_plain_text_not_visible(self, password: str) -> None:
        expect(self.page.locator("body")).not_to_contain_text(password)

    def refresh(self) -> None:
        self.page.reload()
