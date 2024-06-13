"""Initial migration

Revision ID: e00ab2697f7a
Revises: 4e8a185c6c2f
Create Date: 2024-06-12 18:55:12.013598

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e00ab2697f7a'
down_revision: Union[str, None] = '4e8a185c6c2f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('data_source_meta',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('data_source_id', sa.Integer(), nullable=False),
    sa.Column('field_name', sa.String(length=50), nullable=False),
    sa.Column('field_description', sa.Text(), nullable=True),
    sa.ForeignKeyConstraint(['data_source_id'], ['data_source.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('data_source_meta')
    # ### end Alembic commands ###
