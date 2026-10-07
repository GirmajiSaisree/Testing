"""Page object for the application's login and dashboard flows."""

from __future__ import annotations

from typing import Optional

from playwright.sync_api import APIResponse, Page, expect


class LoginPage:
    """Encapsulate login page interactions and observable outcomes."""

    LOGIN_PATH = "/login"
    DASHBOARD_PATH_FRAGMENT = "/dashboard"
    AUTH_API_PATH_FRAGMENT = "/api/auth/login"

    def __init__(self, page: Page, base_url: str) -> None:
        self.page = page
        self.base_url = base_url.rstrip("/")

    @property
    def username_field(self):
        return self.page.get_by_label("Username")

    @property
    def password_field(self):
        return self.page.get_by_label("Password")

    @property
    def submit_button(self):
        return self.page.get_by_role("button", name="Login")

    def open(self) -> None:
        self.page.goto(f"{self.base_url}{self.LOGIN_PATH}")

    def enter_username(self, username: str) -> None:
        self.username_field.fill(username)

    def enter_password(self, password: str) -> None:
        self.password_field.fill(password)

    def submit(self) -> None:
        self.submit_button.click()

    def submit_with_credentials(self, username: str, password: str) -> None:
        self.enter_username(username)
        self.enter_password(password)
        self.submit()

    def expect_logged_in(self) -> None:
        expect(self.page).not_to_have_url(f"{self.base_url}{self.LOGIN_PATH}")

    def expect_dashboard(self) -> None:
        expect(self.page).to_have_url(lambda url: self.DASHBOARD_PATH_FRAGMENT in url)

    def expect_not_logged_in(self) -> None:
        expect(self.page).to_have_url(lambda url: self.LOGIN_PATH in url)

    def expect_login_error(self) -> None:
        expect(self.page.get_by_role("alert")).to_be_visible()

    def expect_validation_for(self, field: str) -> None:
        locator = self.username_field if field == "username" else self.password_field
        expect(locator).to_have_attribute("aria-invalid", "true")

    def expect_password_masked(self) -> None:
        expect(self.password_field).to_have_attribute("type", "password")

    def wait_for_authentication_request(self) -> APIResponse:
        with self.page.expect_response(
            lambda response: self.AUTH_API_PATH_FRAGMENT in response.url
            and response.request.method == "POST"
        ) as response_info:
            self.submit()
        return response_info.value

    def expect_authenticated_after_refresh(self) -> None:
        self.page.reload()
        self.expect_dashboard()

    def configure_runtime_selectors(
        self, username_selector: Optional[str] = None
    ) -> None:
        """Reserved extension point for applications with custom selectors."""
        del username_selector
