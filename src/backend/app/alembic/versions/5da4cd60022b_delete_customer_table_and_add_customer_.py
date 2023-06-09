"""Delete Customer table and add customer column to Project

Revision ID: 5da4cd60022b
Revises: 8332dc02e477
Create Date: 2021-11-29 04:51:19.807390

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '5da4cd60022b'
down_revision = '8332dc02e477'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint('project_customer_id_fkey', 'project', type_='foreignkey')
    op.drop_table('customer')
    op.add_column('project', sa.Column('customer_name', sa.String(), nullable=True))
    op.add_column('project', sa.Column('customer_company', sa.String(), nullable=True))
    op.add_column('project', sa.Column('customer_email', sa.String(), nullable=True))
    op.add_column('project', sa.Column('customer_phone', sa.String(), nullable=True))
    op.drop_column('project', 'customer_id')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('project', sa.Column('customer_id', sa.INTEGER(), autoincrement=False, nullable=True))
    op.create_foreign_key('project_customer_id_fkey', 'project', 'customer', ['customer_id'], ['id'])
    op.drop_column('project', 'customer_phone')
    op.drop_column('project', 'customer_email')
    op.drop_column('project', 'customer_company')
    op.drop_column('project', 'customer_name')
    op.create_table('customer',
    sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('name', sa.VARCHAR(), autoincrement=False, nullable=True),
    sa.Column('email', sa.VARCHAR(), autoincrement=False, nullable=True),
    sa.Column('phone', sa.VARCHAR(), autoincrement=False, nullable=True),
    sa.Column('company', sa.VARCHAR(), autoincrement=False, nullable=True),
    sa.PrimaryKeyConstraint('id', name='customer_pkey')
    )
    # ### end Alembic commands ###
