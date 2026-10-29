from urllib.parse import urlparse, parse_qs
from http.server import HTTPServer, BaseHTTPRequestHandler
from dotenv import load_dotenv
from urllib.parse import urlencode
from threading import Thread, Event
from playwright.sync_api import sync_playwright
import os
import secrets
import pytest
import allure
import hashlib
import base64
import requests

load_dotenv()

reader_username = os.getenv("QA_READER_USERNAME")
reader_password = os.getenv("QA_READER_PASSWORD")
tester_username = os.getenv("QA_TESTER_USERNAME")
tester_password = os.getenv("QA_TESTER_PASSWORD")
AUTH_BASE_URL = "http://localhost:8080"
REALM = "qa-practice"
CLIENT = "qa-practice-api"
REDIRECT_URI = "http://127.0.0.1:8765/callback"
AUTH_URL = f"{AUTH_BASE_URL}/realms/{REALM}/protocol/openid-connect/auth"
TOKEN_URL = f"{AUTH_BASE_URL}/realms/{REALM}/protocol/openid-connect/token"

def build_authorization_request():
    code_verifier = secrets.token_urlsafe()
    verifier_bytes = code_verifier.encode("ascii")
    verifier_hash = hashlib.sha256(verifier_bytes)
    verifier_digest = verifier_hash.digest()
    challenge_encoded = base64.urlsafe_b64encode(verifier_digest)
    code_challenge = challenge_encoded.decode("ascii").rstrip("=")

    auth_params = {
        "response_type" : "code",
        "client_id" : CLIENT,
        "redirect_uri" : REDIRECT_URI,
        "scope" : "openid",
        "code_challenge" : code_challenge,
        "code_challenge_method" : "S256"
    }

    params = urlencode(auth_params)
    authorization_request_url = f"{AUTH_URL}?{params}"

    return authorization_request_url, code_verifier

class CallbackHandler(BaseHTTPRequestHandler):
    authorization_code = None
    authorization_received = Event()

    def do_GET(self):
        parsed_url = urlparse(self.path)
        query_params = parse_qs(parsed_url.query)
        if "code" in query_params:
            CallbackHandler.authorization_code = query_params["code"][0]
            CallbackHandler.authorization_received.set()
            self.send_response(200)
            self.end_headers()

        else:
            self.send_error(400, "Authorization code missing")

def get_access_token(username, password):
    authorization_request_url, code_verifier = build_authorization_request()
    CallbackHandler.authorization_code = None
    CallbackHandler.authorization_received.clear()

    try:
        server = HTTPServer(("127.0.0.1", 8765), CallbackHandler)
        server_thread = Thread(target=server.serve_forever)
        server_thread.start()

        with sync_playwright() as p:
            browser = p.chromium.launch()
            page = browser.new_page()
            page.goto(authorization_request_url)
            page.locator('input[name="username"]').fill(username)
            page.locator('input[name="password"]').fill(password)
            page.locator("#kc-login").click()
            page.wait_for_timeout(2000)
            print("URL after login:", page.url)

            received = CallbackHandler.authorization_received.wait(timeout=30)

            if not received:
                print("Current URL:", page.url)
                print("Page title:", page.title())
                print("Page content:", page.locator("body").inner_text())
                raise TimeoutError("Authorization callback did not arrive")
            
        token_data = {
            "grant_type" : "authorization_code",
            "client_id" : CLIENT,
            "code" : CallbackHandler.authorization_code,
            "redirect_uri" : REDIRECT_URI,
            "code_verifier" : code_verifier
        }

        token_response = requests.post(TOKEN_URL, data=token_data)
        token_response.raise_for_status()
        response_data = token_response.json()
        access_token = response_data["access_token"]
        return access_token

    finally:
        server.shutdown()
        server.server_close()
        server_thread.join()

@pytest.fixture
def reader_access_token():
    access_token = get_access_token(reader_username, reader_password)
    return access_token

@pytest.fixture
def tester_access_token():
    access_token = get_access_token(tester_username, tester_password)
    return access_token

@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item):
    outcome = yield
    report = outcome.get_result()

    if report.when == "call" and report.failed:
        page = item.funcargs.get("page")

        if page is not None:
            allure.attach(
                str(report.longrepr),
                name="Failure details",
                attachment_type=allure.attachment_type.TEXT,
            )
            allure.attach(
                page.screenshot(),
                name="Failure screenshot",
                attachment_type=allure.attachment_type.PNG,
            )
