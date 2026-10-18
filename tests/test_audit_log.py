import requests
import pytest
from app.logging_config import configure_logging
from test_data.user_factory import create_user_data

@pytest.fixture
def create_new_user():
    user = create_user_data("RETAIL")
    response = requests.post("http://127.0.0.1:8000/users", json=user)
    yield user, response

def test_create_post_with_logging(create_new_user):
    user, response = create_new_user

    logger = configure_logging()

    logger.info("Starting test_create_post_with_logging")

    logger.info(f"Response status code: {response.status_code}")
    logger.info(f"Response body: {response.json()}")

    assert response.status_code == 201

    assert "customer_id" in response.json()

    logger.info("Finished test_create_post_with_logging")




    

