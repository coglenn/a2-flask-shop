"""edit fish tickets 2

Revision ID: 6611c9da6b27
Revises: 6a59b01b8943
Create Date: 2023-05-24 19:42:59.007549

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '6611c9da6b27'
down_revision = '6a59b01b8943'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('ticket_entry', 'set_time',
               existing_type=mysql.VARCHAR(length=255),
               type_=sa.Time(),
               existing_nullable=True)
    op.alter_column('ticket_ticket', 'landing_num',
               existing_type=mysql.VARCHAR(length=20),
               nullable=False)
    op.alter_column('ticket_ticket', 'permit_num',
               existing_type=mysql.VARCHAR(length=255),
               nullable=False)
    op.alter_column('ticket_ticket', 'landing_time',
               existing_type=mysql.VARCHAR(length=255),
               type_=sa.Time(),
               existing_nullable=True)
    op.create_foreign_key(None, 'ticket_ticket', 'ticket_entry', ['ticket_entry_id'], ['id'])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'ticket_ticket', type_='foreignkey')
    op.alter_column('ticket_ticket', 'landing_time',
               existing_type=sa.Time(),
               type_=mysql.VARCHAR(length=255),
               existing_nullable=True)
    op.alter_column('ticket_ticket', 'permit_num',
               existing_type=mysql.VARCHAR(length=255),
               nullable=True)
    op.alter_column('ticket_ticket', 'landing_num',
               existing_type=mysql.VARCHAR(length=20),
               nullable=True)
    op.alter_column('ticket_entry', 'set_time',
               existing_type=sa.Time(),
               type_=mysql.VARCHAR(length=255),
               existing_nullable=True)
    # ### end Alembic commands ###
