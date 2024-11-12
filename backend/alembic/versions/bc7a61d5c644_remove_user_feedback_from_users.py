"""remove user feedback from users table

Revision ID: bc7a61d5c644
Revises: bc7a61d5c643
Create Date: 2024-11-12 17:52:00.296970

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = 'bc7a61d5c644'
down_revision: Union[str, None] = 'bc7a61d5c643'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Remove user_feedback column from users table
    op.drop_column('users', 'user_feedback')

def downgrade() -> None:
    # Add back user_feedback column if we need to rollback
    op.add_column('users', sa.Column('user_feedback', sa.JSON(), nullable=True))
