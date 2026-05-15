"""add lcg dynamic cache columns

Revision ID: b2c3d4e5f6a7
Revises: a1b2c3d4e5f6
Create Date: 2026-05-15 12:30:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "b2c3d4e5f6a7"
down_revision: Union[str, None] = "a1b2c3d4e5f6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table("lcg_loans") as batch_op:
        batch_op.add_column(
            sa.Column("interest_due", sa.BigInteger(), nullable=False, server_default="0")
        )
        batch_op.add_column(
            sa.Column(
                "next_interest_ts", sa.BigInteger(), nullable=False, server_default="0"
            )
        )
        batch_op.add_column(
            sa.Column(
                "unpaid_periods", sa.BigInteger(), nullable=False, server_default="0"
            )
        )
        batch_op.add_column(
            sa.Column(
                "dynamic_synced_block",
                sa.BigInteger(),
                nullable=False,
                server_default="0",
            )
        )


def downgrade() -> None:
    with op.batch_alter_table("lcg_loans") as batch_op:
        batch_op.drop_column("dynamic_synced_block")
        batch_op.drop_column("unpaid_periods")
        batch_op.drop_column("next_interest_ts")
        batch_op.drop_column("interest_due")
