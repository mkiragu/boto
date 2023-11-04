"""Make transaction.category_id column nullable

Revision ID: 6bdf9a3dd71b
Revises: 9e1e7a3b376b
Create Date: 2023-11-04 09:02:51.703490

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '6bdf9a3dd71b'
down_revision: Union[str, None] = '9e1e7a3b376b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column('transaction', 'category_id', existing_type=sa.String(), nullable=True)



def downgrade() -> None:
    pass
