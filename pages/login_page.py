"""Page object for the application's login page."""

import os
from urllib.parse import urljoin

from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


class LoginPage:
    """Encapsulates login-page interactions and assertions.

    Override selectors with environment variables when the application uses
    different accessible labels or data-testid values.
    """

    USERNAME = (By.CSS_SELECTOR, os.getenv("LOGIN_USERNAME_SELECTOR", '[name="username"], #username'))
    PASSWORD = (By.CSS_SELECTOR, os.getenv("LOGIN_PASSWORD_SELECTOR", '[name="password"], #password'))
    SUBMIT = (By.CSS_SELECTOR, os.getenv("LOGIN_SUBMIT_SELECTOR", 'button[type="submit"], input[type="submit"]'))
    ERROR = (By.CSS_SELECTOR, os.getenv("LOGIN_ERROR_SELECTOR", '[role="alert"], .error, .alert'))
    USERNAME_ERROR = (By.CSS_SELECTOR, os.getenv("LOGIN_USERNAME_ERROR_SELECTOR", '[data-testid="username-error"], #username-error'))
    PASSWORD_ERROR = (By.CSS_SELECTOR, os.getenv("LOGIN_PASSWORD_ERROR_SELECTOR", '[data-testid="password-error"], #password-error'))

    def __init__(self, driver: WebDriver, base_url: str):
        self.driver = driver
        self.login_url = os.getenv("LOGIN_PATH", "/login")
        self.dashboard_path = os.getenv("DASHBOARD_PATH", "/dashboard")
        self.wait = WebDriverWait(driver, float(os.getenv("SELENIUM_WAIT", "10")))
        self.base_url = base_url

    def open(self) -> "LoginPage":
        self.driver.get(urljoin(self.base_url + "/", self.login_url.lstrip("/")))
        self.wait.until(EC.visibility_of_element_located(self.USERNAME))
        return self

    def enter_username(self, username: str) -> None:
        field = self.wait.until(EC.visibility_of_element_located(self.USERNAME))
        field.clear()
        field.send_keys(username)

    def enter_password(self, password: str) -> None:
        field = self.wait.until(EC.visibility_of_element_located(self.PASSWORD))
        field.clear()
        field.send_keys(password)

    def submit(self) -> None:
        self.wait.until(EC.element_to_be_clickable(self.SUBMIT)).click()

    def submit_credentials(self, username: str, password: str) -> None:
        self.enter_username(username)
        self.enter_password(password)
        self.submit()

    def is_on_dashboard(self) -> bool:
        return self.driver.current_url.rstrip("/").endswith(self.dashboard_path.rstrip("/"))

    def is_on_login_page(self) -> bool:
        return self.login_url.rstrip("/") in self.driver.current_url

    def password_input_type(self) -> str:
        return self.wait.until(EC.presence_of_element_located(self.PASSWORD)).get_attribute("type")

    def password_value(self) -> str:
        return self.wait.until(EC.presence_of_element_located(self.PASSWORD)).get_attribute("value")

    def has_error(self) -> bool:
        return bool(self.driver.find_elements(*self.ERROR))

    def has_username_required_error(self) -> bool:
        return bool(self.driver.find_elements(*self.USERNAME_ERROR)) or self._native_required(self.USERNAME)

    def has_password_required_error(self) -> bool:
        return bool(self.driver.find_elements(*self.PASSWORD_ERROR)) or self._native_required(self.PASSWORD)

    def _native_required(self, locator: tuple[str, str]) -> bool:
        field = self.driver.find_element(*locator)
        return field.get_attribute("required") in {"", "true", "required"} and not field.get_attribute("value")
