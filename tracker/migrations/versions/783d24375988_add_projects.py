"""Add projects."""

import sqlalchemy as sa
from alembic import op

revision: str = "783d24375988"
down_revision: str | None = "76874a1a8dad"
branch_labels: str | None = None
depends_on: str | None = None


def upgrade() -> None:
    op.create_table(
        "projects",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.add_column("tasks", sa.Column("project_id", sa.Integer(), nullable=True))
    op.create_foreign_key(
        "fk_tasks_project_id", "tasks", "projects", ["project_id"], ["id"]
    )


def downgrade() -> None:
    op.drop_constraint("fk_tasks_project_id", "tasks", type_="foreignkey")
    op.drop_column("tasks", "project_id")
    op.drop_table("projects")
