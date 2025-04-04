"""treasure migration

Revision ID: 0bbddadfb3f5
Revises: e679c6e869e2
Create Date: 2025-03-09 17:43:36.057842

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0bbddadfb3f5'
down_revision: Union[str, None] = 'e679c6e869e2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_unique_constraint('uix_user_treasure', 'treasures', ['user_id', 'treasure_value'])
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint('uix_user_treasure', 'treasures', type_='unique')
    # ### end Alembic commands ###
