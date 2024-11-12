"""remove_question_settings

Revision ID: 84d51c51e9ba
Revises: 2d72142c556d
Create Date: 2024-11-12 21:24:53.644454

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '84d51c51e9ba'
down_revision: Union[str, None] = '2d72142c556d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Remove the question_settings column from the users table
    op.drop_column('users', 'question_settings')


def downgrade() -> None:
    # Add the question_settings column back to the users table
    op.add_column('users', sa.Column('question_settings', sa.JSON, nullable=True))
