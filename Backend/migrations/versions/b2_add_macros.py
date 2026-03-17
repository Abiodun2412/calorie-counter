"""add macros and meal_type to food_entries

Revision ID: b2_add_macros
Revises: a1eccb0311e7
Create Date: 2026-03-11
"""

from alembic import op
import sqlalchemy as sa


revision = "b2_add_macros"
down_revision = "a1eccb0311e7"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "food_entries",
        sa.Column("meal_type", sa.String(length=50), nullable=False, server_default="snack")
    )

    op.add_column(
        "food_entries",
        sa.Column("protein", sa.Float(), nullable=False, server_default="0")
    )

    op.add_column(
        "food_entries",
        sa.Column("carbs", sa.Float(), nullable=False, server_default="0")
    )

    op.add_column(
        "food_entries",
        sa.Column("fats", sa.Float(), nullable=False, server_default="0")
    )

    op.alter_column("food_entries", "meal_type", server_default=None)
    op.alter_column("food_entries", "protein", server_default=None)
    op.alter_column("food_entries", "carbs", server_default=None)
    op.alter_column("food_entries", "fats", server_default=None)


def downgrade():
    op.drop_column("food_entries", "fats")
    op.drop_column("food_entries", "carbs")
    op.drop_column("food_entries", "protein")
    op.drop_column("food_entries", "meal_type")