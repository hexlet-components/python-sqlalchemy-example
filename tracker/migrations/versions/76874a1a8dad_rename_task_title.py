"""Rename task title."""

from alembic import op

revision: str = "76874a1a8dad"
down_revision: str | None = "32e016547c7d"
branch_labels: str | None = None
depends_on: str | None = None


def upgrade() -> None:
    op.alter_column("tasks", "title", new_column_name="name")


def downgrade() -> None:
    op.alter_column("tasks", "name", new_column_name="title")
