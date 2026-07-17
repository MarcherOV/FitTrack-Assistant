from typing import TYPE_CHECKING, List
from datetime import datetime , timedelta
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship
from sqlalchemy import DateTime
from sqlalchemy import Interval
from src.db.database import Base

if TYPE_CHECKING:
    from src.models.users import User
    from src.models.exercises import Exercise

class Training(Base):
    __tablename__ = "trainings"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    duration_time: Mapped[timedelta] = mapped_column(Interval, nullable=False)
    exercises: Mapped[List["TrainingExercise"]] = relationship("TrainingExercise", back_populates="training", cascade="all, delete-orphan")
    user: Mapped["User"] = relationship("User", back_populates="trainings")

class TrainingExercise(Base):
    __tablename__ = "training_exercises"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    training_id: Mapped[int] = mapped_column(ForeignKey("trainings.id"), nullable=False)
    exercise_id: Mapped[int] = mapped_column(ForeignKey("exercises.id"), nullable=False)
    sets: Mapped[List["SetsExercise"]] = relationship("SetsExercise", back_populates="training_exercise", cascade="all, delete-orphan")

    training: Mapped["Training"] = relationship("Training", back_populates="exercises")

    exercise: Mapped["Exercise"] = relationship("Exercise")

class SetsExercise(Base):
    __tablename__ = "sets_exercises"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    training_exercise_id: Mapped[int] = mapped_column(ForeignKey("training_exercises.id"), nullable=False)
    set_number: Mapped[int] = mapped_column(nullable=False)
    repetitions: Mapped[int] = mapped_column(nullable=True)
    weight: Mapped[float] = mapped_column(nullable=True)
    distance: Mapped[float] = mapped_column(nullable=True)
    processing_time: Mapped[timedelta] = mapped_column(Interval, nullable=True)
    calories_burned: Mapped[int] = mapped_column(nullable=True)

    training_exercise: Mapped["TrainingExercise"] = relationship("TrainingExercise", back_populates="sets")