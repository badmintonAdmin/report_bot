from sqlalchemy import BigInteger, Boolean, Integer, String
from sqlalchemy.orm import Mapped, mapped_column
from local_db.models.base import BaseModel


class LCGLoanModel(BaseModel):
    __tablename__ = "lcg_loans"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=False)
    borrower: Mapped[str] = mapped_column(String, nullable=False)
    amount: Mapped[int] = mapped_column(BigInteger, nullable=False)
    annual_rate: Mapped[int] = mapped_column(Integer, nullable=False)
    interest_payment_period: Mapped[int] = mapped_column(Integer, nullable=False)
    duration: Mapped[int] = mapped_column(BigInteger, nullable=False)
    borrowed_at: Mapped[int] = mapped_column(BigInteger, nullable=False)
    principal_debt: Mapped[int] = mapped_column(BigInteger, nullable=False)
    borrowed: Mapped[bool] = mapped_column(Boolean, nullable=False)
    repaid: Mapped[bool] = mapped_column(Boolean, nullable=False)
    days_in_period_paid: Mapped[int] = mapped_column(BigInteger, nullable=False)
    last_interest_paid_at: Mapped[int] = mapped_column(BigInteger, nullable=False)
    interest_due: Mapped[int] = mapped_column(BigInteger, nullable=False, default=0)
    next_interest_ts: Mapped[int] = mapped_column(BigInteger, nullable=False, default=0)
    unpaid_periods: Mapped[int] = mapped_column(BigInteger, nullable=False, default=0)
    dynamic_synced_block: Mapped[int] = mapped_column(
        BigInteger, nullable=False, default=0
    )
