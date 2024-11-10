"""add_programming_language_column

Revision ID: 000218390fb2
Revises: 0eaf056cb47e
Create Date: 2024-11-10 11:21:50.114604

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '000218390fb2'
down_revision: Union[str, None] = '0eaf056cb47e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add question_settings column to users table
    op.add_column('users', sa.Column('question_settings', sa.JSON(), server_default='{}'))


def downgrade() -> None:
    # Remove question_settings column from users table
    op.drop_column('users', 'question_settings')
