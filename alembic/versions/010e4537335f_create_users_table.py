"""create_users_table

Revision ID: 010e4537335f
Revises: 
Create Date: 2023-10-22 08:07:42.423538

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '010e4537335f'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

# Define the table name and columns
table_name = "users"

def upgrade() -> None:
    op.create_table(
        table_name,
        sa.Column('id', sa.String, primary_key=True),
        sa.Column('username', sa.String, nullable=False),
        sa.Column('email', sa.String, nullable=False, unique=True),
        sa.Column('first_name', sa.String),
        sa.Column('last_name', sa.String),
        sa.Column('age', sa.Integer, nullable=True),
        sa.Column('gender', sa.String, nullable=True)
    )


def downgrade() -> None:
    op.drop_table(table_name)

