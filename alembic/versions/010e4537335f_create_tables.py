from typing import Sequence, Union

from alembic import op
from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    DECIMAL,
    ForeignKey
)
from sqlalchemy.sql import func


# revision identifiers, used by Alembic.
revision: str = '010e4537335f'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    op.create_table(
        'user',
        Column('uid', String, primary_key=True),
        Column('username', String, nullable=False),
        Column('email', String, nullable=False, unique=True),
        Column('first_name', String),
        Column('last_name', String),
        Column('age', Integer, nullable=True),
        Column('gender', String, nullable=True),
        Column('created_on', DateTime(timezone=True), server_default=func.now()),
        Column('updated_on', DateTime(timezone=True), onupdate=func.now())
    )


    op.create_table(
        'category',
        Column('uid', String, primary_key=True),
        Column('user_id', String, ForeignKey('user.uid'), nullable=False),
        Column('name', String(255), nullable=False),
        Column('created_on', DateTime(timezone=True), server_default=func.now()),
        Column('updated_on', DateTime(timezone=True), onupdate=func.now())
    )

    op.create_table(
        'transaction',
        Column('uid', String, primary_key=True),
        Column('category_id', String, ForeignKey('category.uid'), nullable=False),
        Column('description', String(255), nullable=False),
        Column('amount', DECIMAL, nullable=False),
        Column('created_on', DateTime(timezone=True), server_default=func.now()),
        Column('updated_on', DateTime(timezone=True), onupdate=func.now())
    )


def downgrade() -> None:
    op.drop_table('transactions')
    op.drop_table('category')
    op.drop_table('user')

