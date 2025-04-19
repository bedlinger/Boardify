import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_authentication_and_authorization():
    async with AsyncClient(base_url="http://127.0.0.1:8000/") as client:
        response = await client.post("/register", json={
            "username": "testuser3",
            "password": "password123"
        })
        assert response.status_code == 200

        response = await client.post("/login", data={
            "username": "testuser3",
            "password": "password123"
        })
        assert response.status_code == 200
        token = response.json()["access_token"]

        headers = {"Authorization": f"Bearer {token}"}
        response = await client.post("/boards", json={
            "name": "Test Board",
            "stages": [{"nr": 1, "name": "To Do"}],
            "tags": [{"nr": 1, "name": "Bug"}]
        }, headers=headers)
        assert response.status_code == 200

        response = await client.post("/boards", json={
            "name": "Unauthorized Board",
            "stages": [{"nr": 1, "name": "To Do"}],
            "tags": [{"nr": 1, "name": "Bug"}]
        })
        assert response.status_code == 401