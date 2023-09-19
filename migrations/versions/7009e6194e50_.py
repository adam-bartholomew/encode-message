"""empty message

Revision ID: 7009e6194e50
Revises: c56efb2536e5
Create Date: 2023-09-19 12:11:36.710199

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '7009e6194e50'
down_revision = 'c56efb2536e5'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('saved_messages', schema=None) as batch_op:
        batch_op.alter_column('saved_datetime',
               existing_type=postgresql.TIMESTAMP(),
               type_=sa.DateTime(timezone=True),
               existing_nullable=False,
               existing_server_default=sa.text('now()'))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('saved_messages', schema=None) as batch_op:
        batch_op.alter_column('saved_datetime',
               existing_type=sa.DateTime(timezone=True),
               type_=postgresql.TIMESTAMP(),
               existing_nullable=False,
               existing_server_default=sa.text('now()'))

    # ### end Alembic commands ###