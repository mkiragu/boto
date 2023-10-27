"""Add_transaction_type_column

Revision ID: 07bea2141036
Revises: 068416ea9e61
Create Date: 2023-10-27 11:55:06.119064

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '07bea2141036'
down_revision: Union[str, None] = '068416ea9e61'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('transaction', sa.Column('type', sa.String(length=20), nullable=False))


def downgrade() -> None:
    op.drop_column('transaction', 'type')
