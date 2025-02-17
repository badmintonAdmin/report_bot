from sqlalchemy import DateTime, Text
from sqlalchemy.orm import mapped_column, Mapped
from datetime import datetime, UTC
from local_db.models.base import BaseModel


class TopupModel(BaseModel):
    __tablename__ = "topups"
    date: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(UTC))
    topup: Mapped[str] = mapped_column(Text)
