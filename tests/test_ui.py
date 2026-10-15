import pytest
from playwright.sync_api import expect
from utils.login_page import LoginPage
from test_data.login_data import INVALID_LOGIN_CASES, SUCCESSFUL_LOGIN_CASES

@pytest.fixture
def login_page(page):
    print("Fixture: Prepare login page")
    login_page = LoginPage(page)
    login_page.open()
    yield login_page
    print("Fixture: Cleanup after test")

@pytest.mark.parametrize(
        "username, password, expected_message", 
        SUCCESSFUL_LOGIN_CASES,
    )

def test_login(login_page, page, username, password, expected_message):
    
    login_page.login(username, password)

    expect(login_page.get_success_message()).to_have_text(
        expected_message
    )
    
    expect(page).to_have_url(
        "https://practicetestautomation.com/logged-in-successfully/"
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

    expect(page).to_have_url(
    "https://practicetestautomation.com/practice-test-login/"
)

