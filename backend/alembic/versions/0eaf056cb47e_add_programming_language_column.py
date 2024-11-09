"""add_programming_language_column

Revision ID: 0eaf056cb47e
Revises: 
Create Date: 2024-11-09 20:35:01.981807

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0eaf056cb47e'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('questions', sa.Column('programming_language', sa.String(), nullable=False, server_default='ocaml'))


def downgrade() -> None:
    op.drop_column('questions', 'programming_language')
