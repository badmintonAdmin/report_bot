from sqlalchemy import DateTime, Text
from sqlalchemy.orm import mapped_column, Mapped
from datetime import datetime, UTC
from local_db.models.base import BaseModel


class ReportModel(BaseModel):
    __tablename__ = "reports"
    date: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(UTC))
    date_report: Mapped[datetime] = mapped_column(DateTime)
    report: Mapped[str] = mapped_column(Text)
