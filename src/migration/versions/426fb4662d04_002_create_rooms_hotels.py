"""002 Create rooms hotels

Revision ID: 426fb4662d04
Revises: 6b2543281e38
Create Date: 2024-12-16 13:51:58.848828

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '426fb4662d04'
down_revision: Union[str, None] = '6b2543281e38'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table('rooms',
                    sa.Column('id', sa.Integer(), nullable=False),
                    sa.Column('hotel_id', sa.Integer(), nullable=False),
                    sa.Column('title', sa.String(length=100), nullable=False),
                    sa.Column('description', sa.String(), nullable=True),
                    sa.Column('price', sa.Integer(), nullable=False),
                    sa.Column('quantity', sa.Integer(), nullable=False),
                    sa.ForeignKeyConstraint(['hotel_id'], ['hotels.id'], ),
                    sa.PrimaryKeyConstraint('id')
                    )


def downgrade() -> None:
    op.drop_table('rooms')
