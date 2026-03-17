"""add daily_calorie_goal to people

Revision ID: c3_add_daily_goal
Revises: b2_add_macros
Create Date: 2026-03-17
"""

from alembic import op
import sqlalchemy as sa


revision = "c3_add_daily_goal"
down_revision = "b2_add_macros"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "people",
        sa.Column("daily_calorie_goal", sa.Integer(), nullable=False, server_default="2000")
    )
    op.alter_column("people", "daily_calorie_goal", server_default=None)


def downgrade():
    op.drop_column("people", "daily_calorie_goal")