"""add email password weight height to people

Revision ID: e5_add_user_fields
Revises: d4_add_entry_time
Create Date: 2026-03-18
"""

from alembic import op
import sqlalchemy as sa


revision = "e5_add_user_fields"
down_revision = "d4_add_entry_time"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "people",
        sa.Column("email", sa.String(length=120), nullable=False, server_default="")
    )
    op.add_column(
        "people",
        sa.Column("password", sa.String(length=255), nullable=False, server_default="")
    )
    op.add_column(
        "people",
        sa.Column("weight", sa.Float(), nullable=True)
    )
    op.add_column(
        "people",
        sa.Column("height", sa.Float(), nullable=True)
    )

    op.create_unique_constraint("uq_people_email", "people", ["email"])

    op.alter_column("people", "email", server_default=None)
    op.alter_column("people", "password", server_default=None)


def downgrade():
    op.drop_constraint("uq_people_email", "people", type_="unique")
    op.drop_column("people", "height")
    op.drop_column("people", "weight")
    op.drop_column("people", "password")
    op.drop_column("people", "email")