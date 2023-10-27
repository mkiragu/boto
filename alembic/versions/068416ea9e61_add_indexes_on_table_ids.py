"""Add_indexes_on_table_ids

Revision ID: 068416ea9e61
Revises: 2e77072f3962
Create Date: 2023-10-27 10:33:41.470543

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '068416ea9e61'
down_revision: Union[str, None] = '2e77072f3962'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_index('idx_user_uid', 'user', ['uid'])
    op.create_index('idx_category_uid', 'category', ['uid'])
    op.create_index('idx_transaction_uid', 'transaction', ['uid'])
    op.create_index('idx_wallet_uid', 'wallet', ['uid'])
    pass


def downgrade() -> None:
    op.drop_index('idx_user_uid', table_name='user')
    op.drop_index('idx_category_uid', table_name='category')
    op.drop_index('idx_transaction_uid', table_name='transaction')
    op.drop_index('idx_wallet_uid', table_name='wallet')
    pass
