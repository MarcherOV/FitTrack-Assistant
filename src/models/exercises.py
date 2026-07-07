from typing import List
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship
from src.db.database import Base

class Exercise(Base):
    __tablename__ = "exercises"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(unique=True, nullable=False)
    category_id: Mapped[int] = mapped_column(ForeignKey("categories.id"), nullable=False)
    type_id: Mapped[int] = mapped_column(ForeignKey("types.id"), nullable=False)

    category: Mapped["Category"] = relationship("Category", back_populates="exercises")
    type: Mapped["Type"] = relationship("Type", back_populates="exercises")


class Category(Base):
    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(unique=True, nullable=False)
    exercises: Mapped[List["Exercise"]] = relationship("Exercise", back_populates="category")


class Type(Base):
    __tablename__ = "types"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(unique=True, nullable=False)
    exercises: Mapped[List["Exercise"]] = relationship("Exercise", back_populates="type")