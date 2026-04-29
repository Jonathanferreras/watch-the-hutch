"""add boat detection payload type

Revision ID: 6fb6ac2392a2
Revises: 200dd02283e9
Create Date: 2026-04-29 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = "6fb6ac2392a2"
down_revision: Union[str, Sequence[str], None] = "200dd02283e9"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute("ALTER TYPE eventpayloadtype ADD VALUE IF NOT EXISTS 'BOAT_DETECTION'")


def downgrade() -> None:
    """Downgrade schema."""
    # PostgreSQL enums cannot easily drop individual values in place.
    pass
