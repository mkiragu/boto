"""Add Wallet Table

Revision ID: 2e77072f3962
Revises: 010e4537335f
Create Date: 2023-10-27 08:31:05.019200

"""
from typing import Sequence, Union
from sqlalchemy import (
    Column,
    String,
    DECIMAL,
    ForeignKey,
    DateTime
)

from alembic import op
from sqlalchemy.sql import func


# revision identifiers, used by Alembic.
revision: str = '2e77072f3962'
down_revision: Union[str, None] = '010e4537335f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'wallet',
        Column('uid', String, primary_key=True),
        Column('name', String),
        Column('balance', DECIMAL),
        Column('user_id', String, ForeignKey('user.uid')),
        Column('created_on', DateTime(timezone=True), server_default=func.now()),
        Column('updated_on', DateTime(timezone=True), onupdate=func.now())
    )


def downgrade() -> None:
    op.drop_table('wallet')
