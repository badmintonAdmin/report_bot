from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.ext.asyncio import AsyncAttrs


class BaseModel(AsyncAttrs, DeclarativeBase):
    id: Mapped[int] = mapped_column(primary_key=True)
