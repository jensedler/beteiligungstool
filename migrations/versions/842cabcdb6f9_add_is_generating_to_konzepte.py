"""add is_generating to konzepte

Revision ID: 842cabcdb6f9
Revises:
Create Date: 2026-05-01

"""
from alembic import op
import sqlalchemy as sa


revision = '842cabcdb6f9'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    cols = [c['name'] for c in inspector.get_columns('konzepte')]
    if 'is_generating' not in cols:
        op.add_column(
            'konzepte',
            sa.Column('is_generating', sa.Boolean(), nullable=False, server_default='0'),
        )


def downgrade():
    with op.batch_alter_table('konzepte') as batch_op:
        batch_op.drop_column('is_generating')
