"""empty message

Revision ID: b287ea062f2a
Revises: 0a9fa3d6457b
Create Date: 2019-03-25 08:59:15.188116

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b287ea062f2a'
down_revision = '0a9fa3d6457b'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('ml_stat', sa.Column('num_train_rows', sa.Integer(), nullable=True))
    op.add_column('ml_stat', sa.Column('pred_mean', sa.Float(), nullable=True))
    op.add_column('ml_stat', sa.Column('train_mean', sa.Float(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('ml_stat', 'train_mean')
    op.drop_column('ml_stat', 'pred_mean')
    op.drop_column('ml_stat', 'num_train_rows')
    # ### end Alembic commands ###