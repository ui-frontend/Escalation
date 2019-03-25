"""empty message

Revision ID: f602738e3456
Revises: e18bf712444c
Create Date: 2019-03-25 18:39:42.152785

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f602738e3456'
down_revision = 'e18bf712444c'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('run', sa.Column('_rxn_M_acid', sa.Float(), nullable=True))
    op.add_column('training_run', sa.Column('_rxn_M_acid', sa.Float(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('training_run', '_rxn_M_acid')
    op.drop_column('run', '_rxn_M_acid')
    # ### end Alembic commands ###
