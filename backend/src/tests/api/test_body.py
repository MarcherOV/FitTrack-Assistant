import pytest
from unittest.mock import AsyncMock, MagicMock
from sqlalchemy.exc import IntegrityError
from src.api.dependencies import get_current_user
from src.db.database import get_session
from src.main import app

@pytest.fixture
def mock_current_user():
    user = MagicMock()
    user.id = 1
    return user

@pytest.fixture(autouse=True)
def override_depedencies(mock_current_user):
    mock_session = AsyncMock()
    app.dependency_overrides[get_current_user] = lambda: mock_current_user
    app.dependency_overrides[get_session] = lambda: mock_session
    yield
    app.dependency_overrides.pop(get_current_user, None)
    app.dependency_overrides.pop(get_session, None)

@pytest.fixture
def mock_body_info():
    mock_info = MagicMock()
    mock_info.id = 10
    mock_info.user_id = 1
    mock_info.date = "2026-09-20T10:00:00Z"
    mock_info.weight = 75.5
    return mock_info

@pytest.fixture
def mock_body_measurement():
    mock_measurement = MagicMock()
    mock_measurement.id = 100
    mock_measurement.body_info_id = 10
    mock_measurement.measurements = {"chest": 105.5, "waist": 80.0}
    mock_measurement.body_info.user_id = 1
    return mock_measurement

@pytest.mark.asyncio
async def test_get_body_info_of_user_forbidden(async_client):
    response = await async_client.get("/body-info/users/999/")
    assert response.status_code == 403
    assert response.json()["detail"] == "You don't have permission to view these trainings"

@pytest.mark.asyncio
async def test_get_body_info_not_found(async_client, mocker):
    mocker.patch(
        "src.repositories.body.BodyInfoRepository.get_body_info",
        return_value = None,
        new_callable = AsyncMock
    )
    response = await async_client.get("/body-info/10")
    assert response.status_code == 404
    assert response.json()["detail"] == "The body info does not exist"

@pytest.mark.asyncio
async def test_get_body_info_success(async_client, mocker, mock_body_info):
    mocker.patch(
        "src.repositories.body.BodyInfoRepository.get_body_info",
        return_value = mock_body_info,
        new_callable = AsyncMock
    )

    response = await async_client.get("/body-info/10")
    assert response.status_code == 200

@pytest.mark.asyncio
async def test_create_body_info(async_client, mocker):
    mock_response = {
        "id": 10,
        "user_id": 1,
        "date": "2026-09-20T10:00:00Z",
        "weight": 75.5
    }

    mocker.patch(
        "src.repositories.body.BodyInfoRepository.create_body_info",
        return_value = mock_response,
        new_callable = AsyncMock
    )

    payload = {"user_id": 1, "date": "2026-09-20T10:00:00Z", "weight": 75.5}

    response = await async_client.post("/body-info/", json=payload)

    assert response.status_code == 201
    assert response.json()["id"] == 10
    assert response.json()["weight"] == 75.5

@pytest.mark.asyncio
async def test_create_body_info_integrity_error(async_client, mocker):
    mocker.patch(
        "src.repositories.body.BodyInfoRepository.create_body_info",
        side_effect = IntegrityError("mock", "mock", "mock"),
        new_callable = AsyncMock
    )

    payload = {"user_id": 1, "date": "2026-09-20T10:00:00Z", "weight": 75.5}
    response = await async_client.post("/body-info/", json=payload)

    assert response.status_code == 400
    assert response.json()["detail"] == "The user does not exist"

@pytest.mark.asyncio
async def test_get_all_user_body_info_with_measurements_pagination(async_client, mocker):
    mocker.patch(
        "src.repositories.body.BodyInfoRepository.get_all_user_body_info_with_body_measurements",
        return_value = ([], 0),
        new_callable = AsyncMock
    )

    response = await async_client.get("/body-info/users/1/measurements/?page=1&page_size=5")
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "total" in data
    assert data["page"] == 1


@pytest.mark.asyncio
async def test_create_body_measurement_success(async_client, mocker, mock_body_info):
    mocker.patch(
        "src.repositories.body.BodyInfoRepository.get_body_info",
        return_value = mock_body_info,
        new_callable = AsyncMock
    )

    mock_measurement_response = {
        "id": 100,
        "body_info_id": 10,
        "measurements": {"chest": 105.5, "waist": 80.0}
    }
    mocker.patch(
        "src.repositories.body.BodyMeasurementRepository.create_body_measurements",
        return_value = mock_measurement_response,
        new_callable = AsyncMock
    )

    payload = {
        "body_info_id": 10,
        "measurements": {"chest": 105.5, "waist": 80.0}
    }

    response = await async_client.post("/body-measurements/", json = payload)

    assert response.status_code == 201
    assert response.json()["id"] == 100
    assert response.json()["measurements"]["chest"] == 105.5


@pytest.mark.asyncio
async def test_create_body_measurement_forbidden(async_client, mocker):
    mock_forbidden_info = MagicMock()
    mock_forbidden_info.id = 10
    mock_forbidden_info.user_id = 999

    mocker.patch(
        "src.repositories.body.BodyInfoRepository.get_body_info",
        return_value = mock_forbidden_info,
        new_callable = AsyncMock
    )

    payload = {
        "body_info_id": 10,
        "measurements": {"chest": 105.5}
    }
    response = await async_client.post("/body-measurements/", json = payload)

    assert response.status_code == 403
    assert response.json()["detail"] == "You don't have permission to access this body info"

@pytest.mark.asyncio
async def test_delete_body_measurement_success(async_client, mocker, mock_body_measurement):
    mocker.patch(
        "src.repositories.body.BodyMeasurementRepository.get_body_measurement_with_owner",
        return_value = mock_body_measurement,
        new_callable = AsyncMock
    )

    mocker.patch(
        "src.repositories.body.BodyMeasurementRepository.delete_body_measurements",
        return_value = None,
        new_callable = AsyncMock
    )

    response = await async_client.delete("/body-measurements/100")
    assert response.status_code == 204