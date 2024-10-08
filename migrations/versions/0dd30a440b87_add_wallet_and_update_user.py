"""add wallet and update user

Revision ID: 0dd30a440b87
Revises: 21e6e6ed5e61
Create Date: 2024-08-21 13:01:41.445913

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0dd30a440b87'
down_revision = '21e6e6ed5e61'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('week',
    sa.Column('id', sa.CHAR(length=36), nullable=False),
    sa.Column('expenses', sa.Float(), nullable=True),
    sa.Column('user_id', sa.CHAR(length=36), nullable=True),
    sa.Column('week_start', sa.DateTime(), nullable=True),
    sa.Column('week_end', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.add_column(sa.Column('weeklyPlan', sa.Float(), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.drop_column('weeklyPlan')

    op.drop_table('week')
    # ### end Alembic commands ###
