import pytest
from unittest.mock import AsyncMock
from src.api.dependencies import get_current_user
from src.main import app

@pytest.mark.asyncio
async def test_create_user_success(async_client, mocker):
    mocker.patch(
        "src.repositories.users.UserRepository.get_user_by_telegram_id",
        return_value = None,
        new_callable = AsyncMock
    )

    mock_new_user = {"id": 1, "telegram_id": 123, "username": "test_user"}
    mocker.patch(
        "src.repositories.users.UserRepository.create_user",
        return_value = mock_new_user,
        new_callable = AsyncMock
    )
    payload = {"telegram_id": 123, "username": "test_user"}
    response = await async_client.post("/users/", json=payload)
    
    assert response.status_code == 201
    assert response.json() == mock_new_user

@pytest.mark.asyncio
async def test_create_user_already_exists(async_client, mocker):
    mocker.patch(
        "src.repositories.users.UserRepository.get_user_by_telegram_id",
        return_value = {"id": 1, "telegram_id": 123},
        new_callable = AsyncMock
    )

    payload = {"telegram_id": 123, "username": "test_user"}
    response = await async_client.post("/users/", json=payload)

    assert response.status_code == 409
    assert response.json()["detail"] == "User is already exists"

@pytest.mark.asyncio
async def test_get_all_user_trainings_forbidden(async_client):
    async def override_get_current_user():
        class MockUser:
            id = 999
        return MockUser()
    app.dependency_overrides[get_current_user] = override_get_current_user

    response = await async_client.get("/users/1/trainings/")

    assert response.status_code == 403
    assert response.json()["detail"] == "You don't have permission to view these trainings"

    app.dependency_overrides.pop(get_current_user, None)