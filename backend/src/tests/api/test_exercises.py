import pytest
from unittest.mock import AsyncMock, MagicMock
from sqlalchemy.exc import IntegrityError
from fastapi_cache import FastAPICache
from fastapi_cache.backends.inmemory import InMemoryBackend
from src.api.dependencies import get_current_user
from src.db.database import get_session
from src.main import app

@pytest.fixture(autouse=True)
def setup_depedencies_and_cache():
    FastAPICache.init(InMemoryBackend, prefix="test-cache")

    mock_session = AsyncMock()
    mock_current_user = MagicMock()
    mock_current_user.id = 1

    app.dependency_overrides[get_current_user] = lambda: mock_current_user
    app.dependency_overrides[get_session] = lambda: mock_session

    yield

    app.dependency_overrides.pop(get_current_user, None)
    app.dependency_overrides.pop(get_session, None)
    FastAPICache.reset()

@pytest.fixture
def mock_exercise():
    ex = MagicMock()
    ex.id = 1
    ex.name = "Push Ups"
    ex.category_id = 1
    ex.type_id = 1
    return ex

@pytest.fixture
def mock_category():
    cat = MagicMock()
    cat.id = 1
    cat.name = "Chest"
    cat.exercises = []
    return cat

@pytest.fixture
def mock_type():
    t = MagicMock()
    t.id = 1
    t.name = "Strength"
    t.exercises = []
    return t

@pytest.mark.asyncio
async def test_get_exercise_success(async_client, mocker, mock_exercise):
    mocker.patch(
        "src.repositories.exercises.ExerciseRepository.get_exercise",
        return_value = mock_exercise,
        new_callable = AsyncMock
    )

    response = await async_client.get("/exercises/1")

    assert response.status_code == 200
    assert response.json()["id"] == 1
    assert response.json()["name"] == "Push Ups"

@pytest.mark.asyncio
async def test_get_exercise_not_found(async_client, mocker):
    mocker.patch(
        "src.repositories.exercises.ExerciseRepository.get_exercise",
        return_value = None,
        new_callable = AsyncMock
    )

    response = await async_client.get("/exercises/999")
    assert response.status_code == 404

@pytest.mark.asyncio
async def test_create_exercise_success(async_client, mocker, mock_category, mock_type, mock_exercise):
    mocker.patch(
        "src.repositories.exercises.CategoryRepository.get_category",
        return_value = mock_category,
        new_callable = AsyncMock
    )

    mocker.patch(
        "src.repositories.exercises.TypeRepository.get_type",
        return_value = mock_type,
        new_callable = AsyncMock
    )

    mocker.patch(
        "src.repositories.exercises.ExerciseRepository.create_exercise",
        return_value = mock_exercise,
        new_callable = AsyncMock

    )

    payload = {"name": "Push Ups", "category_id": 1, "type_id": 1}
    response = await async_client.post("/exercises/", json = payload)

    assert response.status_code == 201
    assert response.json()["name"] == "Push Ups"

@pytest.mark.asyncio
async def test_create_exercise_category_not_found(async_client, mocker):
    mocker.patch(
        "src.repositories.exercises.CategoryRepository.get_category",
        return_value = None,
        new_callable = AsyncMock
    )

    payload = {"name": "Push Ups", "category_id": 999, "type_id": 1}
    response = await async_client.post("/exercises/", json = payload)

    assert response.status_code == 404
    assert "does not exist" in response.json()["detail"]

@pytest.mark.asyncio
async def test_create_exercise_integrity_error(async_client, mocker, mock_category, mock_type):
    mocker.patch(
        "src.repositories.exercises.CategoryRepository.get_category",
        return_value = mock_category,
        new_callable = AsyncMock
    )

    mocker.patch(
        "src.repositories.exercises.TypeRepository.get_type",
        return_value = mock_type,
        new_callable = AsyncMock
    )

    mocker.patch(
        "src.repositories.exercises.ExerciseRepository.create_exercise",
        side_effect = IntegrityError("mock", "mock", "mock"),
        new_callable = AsyncMock
    )

    payload = {"name": "Push Ups", "category_id": 1, "type_id": 1}
    response = await async_client.post("/exercises/", json=payload)

    assert response.status_code == 400
    assert "already exists" in response.json()["detail"]

@pytest.mark.asyncio
async def test_delete_exercise_success(async_client, mocker):
    mocker.patch(
        "src.repositories.exercises.ExerciseRepository.delete_exercise",
        return_value = True,
        new_callable = AsyncMock
    )

    response = await async_client.delete("/exercises/1")
    assert response.status_code == 204

@pytest.mark.asyncio
async def test_get_category_success(async_client, mocker, mock_category):
    mocker.patch(
        "src.repositories.exercises.CategoryRepository.get_category",
        return_value = mock_category,
        new_callable = AsyncMock
    )

    response = await async_client.get("/categories/1")
    assert response.status_code == 200
    assert response.json()["name"] == "Chest"

@pytest.mark.asyncio
async def test_get_category_with_exercises(async_client, mocker, mock_category):
    mocker.patch(
        "src.repositories.exercises.CategoryRepository.get_category_with_exercises",
        return_value = mock_category,
        new_callable = AsyncMock
    )

    response = await async_client.get("/categories/1/exercises")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

@pytest.mark.asyncio
async def test_create_category_success(async_client, mocker, mock_category):
    mocker.patch(
        "src.repositories.exercises.CategoryRepository.create_category",
        return_value = mock_category,
        new_callable = AsyncMock
    )

    payload = {"name": "Chest"}
    response = await async_client.post("/categories/", json=payload)

    assert response.status_code == 201
    assert response.json()["id"] == 1

@pytest.mark.asyncio
async def test_get_type_success(async_client, mocker, mock_type):
    mocker.patch(
        "src.repositories.exercises.TypeRepository.get_type",
        return_value = mock_type,
        new_callable = AsyncMock
    )

    response = await async_client.get("/types/1")

    assert response.status_code == 200
    assert response.json()["name"] == "Strength"

@pytest.mark.asyncio
async def test_create_type_success(async_client, mocker, mock_type):
    mocker.patch(
        "src.repositories.exercises.TypeRepository.create_type",
        return_value = mock_type,
        new_callable = AsyncMock
    )

    payload = {"name": "Strength"}
    response = await async_client.post("/types/", json=payload)

    assert response.status_code == 201
    assert response.json()["id"] == 1

@pytest.mark.asyncio
async def test_delete_type_not_found(async_client, mocker):
    mocker.patch(
        "src.repositories.exercises.TypeRepository.delete_type",
        return_value = False,
        new_callable = AsyncMock
    )

    response = await async_client.delete("/types/999")
    assert response.status_code == 404