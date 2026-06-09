"""add use_knowledge_base to system_prompts

Revision ID: 2948f3e0a01e
Revises: 092c81b1003a
Create Date: 2026-06-03 12:16:05.909144

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '2948f3e0a01e'
down_revision = '092c81b1003a'
branch_labels = None
depends_on = None


def upgrade():
    # Guard: Spalte kann durch db.create_all() (seed_questions.py) bereits
    # existieren. Nur hinzufuegen, wenn sie fehlt.
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    columns = [c['name'] for c in inspector.get_columns('system_prompts')]
    if 'use_knowledge_base' not in columns:
        with op.batch_alter_table('system_prompts', schema=None) as batch_op:
            batch_op.add_column(sa.Column('use_knowledge_base', sa.Boolean(), server_default='0', nullable=False))


def downgrade():
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    columns = [c['name'] for c in inspector.get_columns('system_prompts')]
    if 'use_knowledge_base' in columns:
        with op.batch_alter_table('system_prompts', schema=None) as batch_op:
            batch_op.drop_column('use_knowledge_base')
