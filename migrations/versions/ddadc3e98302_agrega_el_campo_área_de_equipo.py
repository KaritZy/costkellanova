"""Agrega el campo Área de equipo

Revision ID: ddadc3e98302
Revises: 0454ac188f4a
Create Date: 2024-10-14 11:54:52.328006

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'ddadc3e98302'
down_revision = '0454ac188f4a'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('cotizacion', schema=None) as batch_op:
        batch_op.add_column(sa.Column('area_equipo', sa.String(length=100), nullable=True))

    with op.batch_alter_table('papelera', schema=None) as batch_op:
        batch_op.add_column(sa.Column('area_equipo', sa.String(length=100), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('papelera', schema=None) as batch_op:
        batch_op.drop_column('area_equipo')

    with op.batch_alter_table('cotizacion', schema=None) as batch_op:
        batch_op.drop_column('area_equipo')

    # ### end Alembic commands ###
