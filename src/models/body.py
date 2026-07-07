from typing import List
from datetime import datetime
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship
from sqlalchemy import DateTime
from sqlalchemy.dialects.postgresql import JSONB
from src.db.database import Base
from src.models.users import User

class BodyInfo(Base):
    __tablename__ = "body_info"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    weight: Mapped[float] = mapped_column(nullable=True)

    user: Mapped["User"] = relationship("User", back_populates="body_info")

class BodyMeasurement(Base):
    __tablename__ = "body_measurements"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    body_info_id: Mapped[int] = mapped_column(ForeignKey("body_info.id"), nullable=False)
    measurements: Mapped[dict] = mapped_column(JSONB)