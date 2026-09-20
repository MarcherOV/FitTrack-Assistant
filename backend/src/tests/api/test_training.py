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
def override_dependencies(mock_current_user):
    mock_session = AsyncMock()
    app.dependency_overrides[get_current_user] = lambda: mock_current_user
    app.dependency_overrides[get_session] = lambda: mock_session
    yield
    app.dependency_overrides.pop(get_current_user, None)
    app.dependency_overrides.pop(get_session, None)

@pytest.fixture
def valid_training_payload():
    return {
        "user_id": 1,
        "date": "2026-09-19T10:00:00Z",
        "duration_time": "PT1H30M",
        "exercises": [
            {
                "exercise_id": 10,
                "sets": [
                    {"set_number": 1, "repetitions": 12, "weight": 50.5}
                ]
            }
        ]
    }

@pytest.fixture
def mock_training_response():
    return {
        "id": 1,
        "user_id": 1,
        "date": "2026-09-19T10:00:00Z",
        "duration_time": "PT1H30M",
        "exercises": [
            {
                "id": 100,
                "training_id": 1,
                "exercise_id": 10,
                "exercise": {"id": 10, "name": "Squats", "type": "strength", "category_id": 1, "type_id": 1}, 
                "sets": [
                    {
                        "id": 1000,
                        "training_exercise_id": 100,
                        "set_number": 1,
                        "repetitions": 12,
                        "weight": 50.5,
                        "distance": None,
                        "processing_time": None,
                        "calories_burned": None
                    }
                ]
            }
        ]
    }

@pytest.mark.asyncio
async def test_create_training_success(async_client, mocker, valid_training_payload, mock_training_response):
    mock_training = {"id": 1, "name": "Leg Day", "user_id": 1}
    mocker.patch(
        "src.repositories.training.TrainingRepository.create_training",
        return_value = mock_training_response,
        new_callable = AsyncMock
    )

    response = await async_client.post("/trainings/", json=valid_training_payload)

    assert response.status_code == 201
    assert response.json()["id"] == 1
    assert response.json()["duration_time"] == "PT1H30M"

@pytest.mark.asyncio
async def test_get_training_success(async_client, mocker, mock_training_response):
    mock_training = MagicMock()
    mock_training.id = 1
    mock_training.user_id = 1
    mock_training.date = "2026-09-19T10:00:00Z"
    mock_training.duration_time = "PT1H30M"
    mock_training.exercises = []

    mocker.patch(
        "src.repositories.training.TrainingRepository.get_training",
        return_value = mock_training,
        new_callable = AsyncMock
    )

    response = await async_client.get("/trainings/1")
    assert response.status_code == 200

@pytest.mark.asyncio
async def test_get_training_forbidden(async_client, mocker):
    mock_training = MagicMock()
    mock_training.id = 1
    mock_training.user_id = 999

    mocker.patch(
        "src.repositories.training.TrainingRepository.get_training",
        return_value = mock_training,
        new_callable = AsyncMock
    )

    response = await async_client.get("/trainings/1")
    assert response.status_code == 403
    assert response.json()["detail"] == "You don't have permission to access this training"

@pytest.mark.asyncio
async def test_create_training_exercise_integrity_error(async_client, mocker):
    mock_training = MagicMock()
    mock_training.id = 1
    mock_training.user_id = 1

    mocker.patch(
        "src.repositories.training.TrainingRepository.get_training",
        return_value = mock_training,
        new_callable = AsyncMock
    )

    mocker.patch(
        "src.repositories.training.TrainingExerciseRepository.create_training_exercise",
        side_effect = IntegrityError("mock", "mock", "mock"),
        new_callable = AsyncMock
    )

    payload = {
        "exercise_id": 999,
        "sets": [{"set_number": 1, "repetitions": 10}]
    }

    response = await async_client.post("/trainings/1/exercises", json=payload)

    assert response.status_code == 400
    assert response.json()["detail"] == "User ID or Exercise ID does not exist."

@pytest.mark.asyncio
async def test_create_set_success(async_client, mocker):
    mock_training_exercise = MagicMock()
    mock_training_exercise.training.user_id = 1

    mock_set_response = {
        "id": 1000,
        "training_exercise_id": 100,
        "set_number": 2,
        "repetitions": 8,
        "weight": 60.0,
        "distance": None,
        "processing_time": None,
        "calories_burned": None
    }

    mocker.patch(
        "src.repositories.training.TrainingExerciseRepository.get_training_exercise_with_owner",
        return_value = mock_training_exercise,
        new_callable = AsyncMock
    )

    mocker.patch(
        "src.repositories.training.SetsExerciseRepository.create_set_exercise",
        return_value = mock_set_response,
        new_callable = AsyncMock
    )

    payload = {"set_number": 2, "repetitions": 8, "weight": 60.0}
    response = await async_client.post("/training-exercises/100/sets", json=payload)

    assert response.status_code == 201
    assert response.json()["id"] == 1000
    assert response.json()["weight"] == 60.0

@pytest.mark.asyncio
async def test_delete_set_success(async_client, mocker):
    mock_set = MagicMock()
    mock_set.training_exercise.training.user_id = 1

    mocker.patch(
        "src.repositories.training.SetsExerciseRepository.get_set_exercise_with_owner",
        return_value = mock_set,
        new_callable = AsyncMock
    )

    mocker.patch(
        "src.repositories.training.SetsExerciseRepository.delete_set_exercise",
        return_value = None,
        new_callable = AsyncMock
    )

    response = await async_client.delete("/sets/1000")
    assert response.status_code == 204