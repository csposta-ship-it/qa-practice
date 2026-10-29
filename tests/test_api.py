from test_data.login_data import dummy_user
from test_data.user_factory import create_user_data
import requests

BASE_URL = "http://127.0.0.1:8000"

def test_health_check():
    response = requests.get(f"{BASE_URL}/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

def test_post_without_authorization():
    response = requests.post(
        f"{BASE_URL}/users",
        json= dummy_user
    )

    assert response.status_code == 401

def test_post_without_permission(reader_access_token):
    new_user = create_user_data("RETAIL")
    response = requests.post(
        f"{BASE_URL}/users",
        headers= {"Authorization": f"Bearer {reader_access_token}"},
        json= new_user
    )

    assert response.status_code == 403

def test_post_with_permission(tester_access_token):
    new_user = create_user_data("RETAIL")
    response = requests.post(
        f"{BASE_URL}/users",
        headers= {"Authorization": f"Bearer {tester_access_token}"},
        json= new_user
    )

    assert response.status_code == 201