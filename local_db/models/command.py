from sqlalchemy import String, Text
from sqlalchemy.orm import mapped_column, Mapped
from .base import BaseModel


class CommandModel(BaseModel):
    __tablename__ = "commands"
    command: Mapped[str] = mapped_column(String(50))
    description: Mapped[str] = mapped_column(Text)
