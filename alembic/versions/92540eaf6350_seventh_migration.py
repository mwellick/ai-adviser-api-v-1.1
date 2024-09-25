"""Seventh migration

Revision ID: 92540eaf6350
Revises: 6f16466315ae
Create Date: 2024-09-25 14:55:25.319661

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '92540eaf6350'
down_revision: Union[str, None] = '6f16466315ae'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('chats', schema=None) as batch_op:
        batch_op.drop_column('is_saved')

    with op.batch_alter_table('messages', schema=None) as batch_op:
        batch_op.add_column(sa.Column('is_saved', sa.Boolean(), nullable=False))

    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('messages', schema=None) as batch_op:
        batch_op.drop_column('is_saved')

    with op.batch_alter_table('chats', schema=None) as batch_op:
        batch_op.add_column(sa.Column('is_saved', sa.BOOLEAN(), nullable=False))

    # ### end Alembic commands ###
