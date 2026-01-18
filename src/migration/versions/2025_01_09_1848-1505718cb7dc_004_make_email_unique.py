"""004 Make email unique

Revision ID: 1505718cb7dc
Revises: ed77240b4dbc
Create Date: 2025-01-09 18:48:16.463761

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "1505718cb7dc"
down_revision: Union[str, None] = "ed77240b4dbc"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_unique_constraint(None, "users", ["email"])


def downgrade() -> None:
    op.drop_constraint(None, "users", type_="unique")
