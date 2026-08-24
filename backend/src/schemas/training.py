from pydantic import BaseModel, ConfigDict
from datetime import datetime
from datetime import timedelta
from src.schemas.exercises import ExerciseGET

class BaseORMModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)

class SetsExercisePOST(BaseModel):
    set_number: int
    repetitions: int | None = None
    weight: float | None = None
    distance: float | None = None
    processing_time: timedelta | None = None
    calories_burned: int | None = None

class SetsExerciseGET(SetsExercisePOST, BaseORMModel):
    id: int
    training_exercise_id: int


class SetsExerciseUPDATE(BaseModel):
    training_exercise_id: int | None = None
    set_number: int | None = None
    repetitions: int | None = None
    weight: float | None = None
    distance: float | None = None
    processing_time: timedelta | None = None
    calories_burned: int | None = None

class TrainingExercisePOST(BaseModel):
    exercise_id: int
    sets: list[SetsExercisePOST]

class TrainingExerciseGET(TrainingExercisePOST, BaseORMModel):
    id: int
    training_id: int
    exercise: ExerciseGET
    sets: list[SetsExerciseGET]


class TrainingExerciseUPDATE(BaseModel):
    training_id: int | None = None
    exercise_id: int | None = None


class TrainingPOST(BaseModel):
    user_id: int
    date: datetime
    duration_time: timedelta
    exercises: list[TrainingExercisePOST]


class TrainingGET(TrainingPOST, BaseORMModel):
    id: int
    exercises: list[TrainingExerciseGET]


class TrainingUPDATE(BaseModel):
    date: datetime | None = None
    duration_time: timedelta | None = None

