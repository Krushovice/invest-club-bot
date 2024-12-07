"""add pay id to Payment table

Revision ID: c8652f719573
Revises: 
Create Date: 2024-12-07 12:23:14.542408

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c8652f719573'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('payments', sa.Column('pay_id', sa.BigInteger(), nullable=False))
    op.create_unique_constraint(None, 'payments', ['pay_id'])
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'payments', type_='unique')
    op.drop_column('payments', 'pay_id')
    # ### end Alembic commands ###
