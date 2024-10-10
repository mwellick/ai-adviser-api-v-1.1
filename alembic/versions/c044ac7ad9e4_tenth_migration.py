"""Tenth migration

Revision ID: c044ac7ad9e4
Revises: 19b6c9189c5d
Create Date: 2024-10-10 21:50:43.674167

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c044ac7ad9e4'
down_revision: Union[str, None] = '19b6c9189c5d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('saved_messages', schema=None) as batch_op:
        batch_op.alter_column('chat_id',
               existing_type=sa.INTEGER(),
               nullable=True)

    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('saved_messages', schema=None) as batch_op:
        batch_op.alter_column('chat_id',
               existing_type=sa.INTEGER(),
               nullable=False)

    # ### end Alembic commands ###
