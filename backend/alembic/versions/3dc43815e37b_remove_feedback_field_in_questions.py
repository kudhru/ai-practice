"""remove_feedback_field_in_questions

Revision ID: 3dc43815e37b
Revises: fa257be44ced
Create Date: 2024-11-12 21:56:33.191573

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '3dc43815e37b'
down_revision: Union[str, None] = 'fa257be44ced'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Remove the 'feedback' column from the 'questions' table
    op.drop_column('user_solved_questions', 'user_feedback')


def downgrade() -> None:
    # Add back the 'feedback' column to the 'questions' table
    op.add_column('user_solved_questions', sa.Column('user_feedback', sa.JSON(), nullable=True))
