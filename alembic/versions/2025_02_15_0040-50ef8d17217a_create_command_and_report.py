"""create command and report

Revision ID: 50ef8d17217a
Revises:
Create Date: 2025-02-15 00:40:36.382175

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "50ef8d17217a"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:

    op.create_table(
        "commands",
        sa.PrimaryKeyConstraint("id"),
        sa.Column("command", sa.String(length=50), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("id", sa.Integer(), nullable=False),
    )
    op.create_table(
        "reports",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("date", sa.DateTime(), nullable=False),
        sa.Column("date_report", sa.DateTime(), nullable=False),
        sa.Column("report", sa.Text(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:

    op.drop_table("reports")
    op.drop_table("commands")
