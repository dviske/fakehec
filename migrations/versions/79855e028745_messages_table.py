"""messages table

Revision ID: 79855e028745
Revises: 40aa067c56d1
Create Date: 2025-04-05 13:40:57.560451

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '79855e028745'
down_revision = '40aa067c56d1'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('message',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('received_at', sa.DateTime(), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False),
    sa.Column('received_from', sa.String(length=50), nullable=False),
    sa.Column('content', sa.Text(), nullable=True),
    sa.Column('collector_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['collector_id'], ['collector.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('message')
    # ### end Alembic commands ###
