"""create top up

Revision ID: 7e87f172b9e4
Revises: 50ef8d17217a
Create Date: 2025-02-17 12:20:39.753007

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "7e87f172b9e4"
down_revision: Union[str, None] = "50ef8d17217a"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "topups",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("date", sa.DateTime(), nullable=False),
        sa.Column("topup", sa.Text(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:

    op.drop_table("topups")
