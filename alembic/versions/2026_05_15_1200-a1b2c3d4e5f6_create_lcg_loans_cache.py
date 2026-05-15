"""create lcg loans cache

Revision ID: a1b2c3d4e5f6
Revises: 7e87f172b9e4
Create Date: 2026-05-15 12:00:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "a1b2c3d4e5f6"
down_revision: Union[str, None] = "7e87f172b9e4"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "lcg_loans",
        sa.Column("id", sa.Integer(), nullable=False, autoincrement=False),
        sa.Column("borrower", sa.String(), nullable=False),
        sa.Column("amount", sa.BigInteger(), nullable=False),
        sa.Column("annual_rate", sa.Integer(), nullable=False),
        sa.Column("interest_payment_period", sa.Integer(), nullable=False),
        sa.Column("duration", sa.BigInteger(), nullable=False),
        sa.Column("borrowed_at", sa.BigInteger(), nullable=False),
        sa.Column("principal_debt", sa.BigInteger(), nullable=False),
        sa.Column("borrowed", sa.Boolean(), nullable=False),
        sa.Column("repaid", sa.Boolean(), nullable=False),
        sa.Column("days_in_period_paid", sa.BigInteger(), nullable=False),
        sa.Column("last_interest_paid_at", sa.BigInteger(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "sync_state",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("value", sa.String(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("sync_state")
    op.drop_table("lcg_loans")
