import requests
from utils.api_client import APIClient


client = APIClient(
    "https://jsonplaceholder.typicode.com"
)

def test_get_users():

    response = client.get("/users")

    assert response.status_code == 200

    data = response.json()

    assert len(data) > 0

def test_create_post():
    response = client.post(
    "/posts",
    {
        "title": "test",
        "body": "hello",
        "userId": 1
    }
)

    assert response.status_code == 201

def test_create_post_without_title():
    response = client.post(
        "/posts",
        {
            "body": "hello",
            "userId": 1
        }
    )

    assert response.status_code == 201