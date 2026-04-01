"""add payload_type to event

Revision ID: 200dd02283e9
Revises:
Create Date: 2026-03-31 16:51:40.801425

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "200dd02283e9"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


payload_type_enum = postgresql.ENUM(
    "BRIDGE_STATE",
    "DEVICE_TELEMETRY",
    name="eventpayloadtype",
)


def upgrade() -> None:
    """Upgrade schema."""
    bind = op.get_bind()
    payload_type_enum.create(bind, checkfirst=True)

    op.add_column(
        "event",
        sa.Column("payloadType", payload_type_enum, nullable=True),
    )

    # Backfill existing rows based on the payload shape already stored in JSON.
    op.execute(
        """
        UPDATE event
        SET "payloadType" = CASE
            WHEN payload::jsonb ? 'status' AND payload::jsonb ? 'confidence'
                THEN 'BRIDGE_STATE'::eventpayloadtype
            ELSE 'DEVICE_TELEMETRY'::eventpayloadtype
        END
        """
    )

    op.alter_column("event", "payloadType", nullable=False)
    op.create_index(op.f("ix_event_payloadType"), "event", ["payloadType"], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f("ix_event_payloadType"), table_name="event")
    op.drop_column("event", "payloadType")
    payload_type_enum.drop(op.get_bind(), checkfirst=True)
