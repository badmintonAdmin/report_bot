from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column
from local_db.models.base import BaseModel


class SyncStateModel(BaseModel):
    __tablename__ = "sync_state"
    id: Mapped[str] = mapped_column(String, primary_key=True)
    value: Mapped[str] = mapped_column(String, nullable=False)
