from typing import TYPE_CHECKING, List
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship
from sqlalchemy import BigInteger
from src.db.database import Base

if TYPE_CHECKING:
    from src.models.training import Training
    from src.models.body import BodyInfo

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(unique=True, nullable=True)
    telegram_id: Mapped[int] = mapped_column(BigInteger, unique=True, nullable=True)
    trainings: Mapped[List["Training"]] = relationship("Training", back_populates="user")
    body_info: Mapped[List["BodyInfo"]] = relationship("BodyInfo", back_populates="user")