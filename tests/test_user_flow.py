import pytest
import requests

def test_user_flow(server_url, user_token):
    # Use the token and server_url directly
    token = user_token

    # Define your test data
    url_data_public = {"target_url": "https://google.com", "type": "public"}
    url_data_private = {"target_url": "https://yahoo.com", "type": "private"}

    # Headers for authentication
    headers = {"Authorization": f"Bearer {token}"}

    # Create public URL
    response = requests.post(
        f"{server_url}/v1/url",
        json=url_data_public,
        headers=headers
    )
    assert response.status_code == 201
    public_key = response.json().get("key")
    assert public_key is not None

    # Create private URL
    response = requests.post(
        f"{server_url}/v1/url",
        json=url_data_private,
        headers=headers
    )
    assert response.status_code == 201
    private_key = response.json().get("key")
    assert private_key is not None

    # Check user links
    response = requests.get(
        f"{server_url}/v1/user/status",
        headers=headers
    )
    assert response.status_code == 200
    links = response.json()
    assert any(link["key"] == public_key for link in links)
    assert any(link["key"] == private_key for link in links)

    # Delete public URL
    response = requests.delete(
        f"{server_url}/v1/url/{public_key}",
        headers=headers
    )
    assert response.status_code == 200

    # Check user links again
    response = requests.get(
        f"{server_url}/v1/user/status",
        headers=headers
    )
    assert response.status_code == 200
    links = response.json()
    assert not any(link["key"] == public_key for link in links)
    assert any(link["key"] == private_key for link in links)
