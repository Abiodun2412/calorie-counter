"""add entry_time to food_entries

Revision ID: d4_add_entry_time
Revises: c3_add_daily_goal
Create Date: 2026-03-18
"""

from alembic import op
import sqlalchemy as sa


revision = "d4_add_entry_time"
down_revision = "c3_add_daily_goal"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "food_entries",
        sa.Column(
            "entry_time",
            sa.Time(),
            nullable=False,
            server_default=sa.text("'00:00:00'")
        )
    )
    op.alter_column("food_entries", "entry_time", server_default=None)


def downgrade():
    op.drop_column("food_entries", "entry_time")