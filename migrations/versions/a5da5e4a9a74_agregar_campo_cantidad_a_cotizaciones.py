"""Agregar campo cantidad a cotizaciones

Revision ID: a5da5e4a9a74
Revises: 9dc1030aabaf
Create Date: 2024-09-25 02:11:16.954501

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a5da5e4a9a74'
down_revision = '9dc1030aabaf'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('cotizacion') as batch_op:
        # Agregar la columna cantidad con un valor por defecto de 1
        batch_op.add_column(sa.Column('cantidad', sa.Integer(), nullable=False, server_default="1"))


    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('cotizacion', schema=None) as batch_op:
        batch_op.drop_column('cantidad')

    # ### end Alembic commands ###
