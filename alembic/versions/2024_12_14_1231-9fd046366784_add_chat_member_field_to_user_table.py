"""Add chat_member field to user table

Revision ID: 9fd046366784
Revises: 68fdd75a7eec
Create Date: 2024-12-14 12:31:17.387698

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '9fd046366784'
down_revision: Union[str, None] = '68fdd75a7eec'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('users', sa.Column('chat_member', sa.Boolean(), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('users', 'chat_member')
    # ### end Alembic commands ###
