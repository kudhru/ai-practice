"""add_user_feedback

Revision ID: bc7a61d5c643
Revises: 000218390fb2
Create Date: 2024-11-12 17:42:00.296970

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = 'bc7a61d5c643'
down_revision: Union[str, None] = '000218390fb2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add user_feedback column with JSON type
    op.add_column('user', sa.Column('user_feedback', sa.JSON(), nullable=True))

def downgrade() -> None:
    # Remove user_feedback column if we need to rollback
    op.drop_column('user', 'user_feedback')
