import pytest
from playwright.sync_api import expect
from utils.login_page import LoginPage
from test_data.login_data import INVALID_LOGIN_CASES

@pytest.fixture
def login_page(page):
    login_page = LoginPage(page)
    login_page.open()
    return login_page


def test_login(login_page):
    
    login_page.login("student", "Password123")

    expect(login_page.get_success_message()).to_have_text(
        "Logged In Successfully"
    )

@pytest.mark.parametrize(
        "username, password, expected_error", 
        INVALID_LOGIN_CASES
    )
def test_login_with_invalid_credentials(
        page, login_page, username, password, expected_error   
    ):
    
    login_page.login(username, password)

    expect(login_page.get_error_message()).to_have_text(
        expected_error
    )

    expect(page).not_to_have_url(
    "https://practicetestautomation.com/logged-in-successfully/"
    )