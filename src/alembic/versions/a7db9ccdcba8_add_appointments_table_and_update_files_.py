"""Add appointments table and update files table

Revision ID: a7db9ccdcba8
Revises: de84cb899fc5
Create Date: 2025-07-29 20:00:48.466395

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision: str = 'a7db9ccdcba8'
down_revision: Union[str, None] = 'de84cb899fc5'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('appointments',
    sa.Column('id', sa.VARCHAR(length=36), nullable=False),
    sa.Column('name', sa.String(length=255), nullable=False),
    sa.Column('date', sa.DateTime(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_appointments_name'), 'appointments', ['name'], unique=True)
    op.add_column('files', sa.Column('filename', sa.String(length=255), nullable=False))
    op.add_column('files', sa.Column('appointment_id', sa.VARCHAR(length=36), nullable=False))
    op.drop_index('ix_files_appointment', table_name='files')
    op.create_foreign_key('fk_files_appointment_id', 'files', 'appointments', ['appointment_id'], ['id'])
    op.drop_column('files', 'appointment')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('files', sa.Column('appointment', mysql.VARCHAR(length=255), nullable=False))
    op.drop_constraint('fk_files_appointment_id', 'files', type_='foreignkey')
    op.create_index('ix_files_appointment', 'files', ['appointment'], unique=False)
    op.drop_column('files', 'appointment_id')
    op.drop_column('files', 'filename')
    op.drop_index(op.f('ix_appointments_name'), table_name='appointments')
    op.drop_table('appointments')
    # ### end Alembic commands ###
