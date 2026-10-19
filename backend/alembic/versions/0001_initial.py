"""Initial persistent records and session event log."""

import sqlalchemy as sa

from alembic import op

revision = "0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "records",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("kind", sa.String(30), nullable=False),
        sa.Column("payload", sa.Text(), nullable=False),
    )
    op.create_index("ix_records_kind", "records", ["kind"])
    op.create_table(
        "events",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("session_id", sa.String(36), sa.ForeignKey("records.id"), nullable=False),
        sa.Column("stage", sa.String(50), nullable=False),
        sa.Column("status", sa.String(30), nullable=False),
    )
    op.create_index("ix_events_session_id", "events", ["session_id"])


def downgrade():
    op.drop_table("events")
    op.drop_table("records")
