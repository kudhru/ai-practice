"""update_question_settings

Revision ID: fa257be44ced
Revises: 9c4b4939c448
Create Date: 2024-11-12 21:37:19.026379

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'fa257be44ced'
down_revision: Union[str, None] = '9c4b4939c448'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Update question_settings column to use MutableDict
    op.alter_column('users', 'question_settings', 
                    type_=sa.JSON,
                    postgresql_using='question_settings::json',
                    existing_nullable=True,
                    server_default='{}')


def downgrade() -> None:
    # Revert question_settings column back to regular JSON
    op.alter_column('users', 'question_settings',
                    type_=sa.JSON,
                    postgresql_using='question_settings::json',
                    existing_nullable=True,
                    server_default=None)
