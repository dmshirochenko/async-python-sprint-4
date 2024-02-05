import os
import random
import string
import pytest
import requests
from dotenv import load_dotenv

load_dotenv()

@pytest.fixture(scope="session")
def server_url():
    return os.getenv("SERVER_URL", "http://localhost:8000")

@pytest.fixture(scope="session")
def user_token(server_url):
    random_user_name = ''.join(random.choices(string.ascii_lowercase + string.digits, k=10))
    user_data = {"username": f"testuser_{random_user_name}"}
    response = requests.post(f"{server_url}/v1/user/registration", json=user_data)
    print(response.json()   )
    assert response.status_code == 201
    return response.json().get("token")
