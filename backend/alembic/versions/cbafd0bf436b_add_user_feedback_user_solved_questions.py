"""add_user_feedback_user_solved_questions

Revision ID: cbafd0bf436b
Revises: bc7a61d5c644
Create Date: 2024-11-12 17:54:23.819655

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'cbafd0bf436b'
down_revision: Union[str, None] = 'bc7a61d5c644'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add user_feedback column to user_solved_questions table
    op.add_column('user_solved_questions', sa.Column('user_feedback', sa.JSON(), nullable=True))

def downgrade() -> None:
    # Remove user_feedback column if we need to rollback
    op.drop_column('user_solved_questions', 'user_feedback')
