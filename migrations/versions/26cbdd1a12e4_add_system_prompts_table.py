"""add system_prompts table

Revision ID: 26cbdd1a12e4
Revises: 842cabcdb6f9
Create Date: 2026-05-11 20:26:25.128899

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '26cbdd1a12e4'
down_revision = '842cabcdb6f9'
branch_labels = None
depends_on = None


def upgrade():
    # Guard: Tabelle kann durch db.create_all() (seed_questions.py) bereits
    # existieren. Nur anlegen, wenn sie fehlt, damit bestehende Instanzen
    # nicht beschaedigt werden.
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    if 'system_prompts' not in inspector.get_table_names():
        op.create_table('system_prompts',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
        )


def downgrade():
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    if 'system_prompts' in inspector.get_table_names():
        op.drop_table('system_prompts')
