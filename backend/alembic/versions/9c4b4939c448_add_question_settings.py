"""add_question_settings

Revision ID: 9c4b4939c448
Revises: 84d51c51e9ba
Create Date: 2024-11-12 21:29:02.806259

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '9c4b4939c448'
down_revision: Union[str, None] = '84d51c51e9ba'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add the question_settings column to the users table
    op.add_column('users', sa.Column('question_settings', sa.JSON, nullable=True))


def downgrade() -> None:
    # Remove the question_settings column from the users table
    op.drop_column('users', 'question_settings')
