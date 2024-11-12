"""update_question_settings

Revision ID: 2d72142c556d
Revises: cbafd0bf436b
Create Date: 2024-11-12 21:21:05.154173

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSON


# revision identifiers, used by Alembic.
revision: str = '2d72142c556d'
down_revision: Union[str, None] = 'cbafd0bf436b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Alter the question_settings column to use MutableDict
    op.alter_column('users', 'question_settings', type_=sa.JSON, postgresql_using='question_settings::json')


def downgrade() -> None:
    # Revert the question_settings column to its original state
    op.alter_column('users', 'question_settings', type_=sa.JSON, postgresql_using='question_settings::json')
