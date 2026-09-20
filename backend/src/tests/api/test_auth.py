import pytest
from unittest.mock import AsyncMock

@pytest.mark.asyncio
async def test_authenticate_via_telegram_success(async_client, mocker):
    mocker.patch(
        "src.api.routers.auth.verify_telegram_web_app_data",
        return_value={"id": 123456, "username": "testuser"}
    )

    mock_db_user = mocker.MagicMock()
    mock_db_user.id = 1
    mocker.patch(
        "src.repositories.users.UserRepository.get_user_by_telegram_id",
        return_value=mock_db_user,
        new_callable=AsyncMock
    )
    payload = {"initData": "fake_telegram_init_data"}
    response = await async_client.post("/api/v1/auth/telegram", json=payload)

    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["user_id"] == 1

@pytest.mark.asyncio
async def test_authenticate_via_telegram_invalid_data(async_client, mocker):
    mocker.patch("src.api.routers.auth.verify_telegram_web_app_data",
                 return_value=None)

    payload = {"initData": "invalid_data"}
    response = await async_client.post("/api/v1/auth/telegram", json=payload)

    assert response.status_code == 401
    assert response.json()["detail"] == "Could not validate Telegram data"