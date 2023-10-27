"""Add_wallet_currency_column

Revision ID: 9e1e7a3b376b
Revises: 07bea2141036
Create Date: 2023-10-27 16:04:18.311553

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '9e1e7a3b376b'
down_revision: Union[str, None] = '07bea2141036'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('wallet', sa.Column('currency', sa.String(length=5)))



def downgrade() -> None:
    op.drop_column('wallet', 'currency')

