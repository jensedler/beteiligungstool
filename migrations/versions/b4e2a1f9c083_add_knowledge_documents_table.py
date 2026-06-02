"""add knowledge_documents table

Revision ID: b4e2a1f9c083
Revises: 842cabcdb6f9
Create Date: 2026-05-01

"""
from alembic import op
import sqlalchemy as sa


revision = 'b4e2a1f9c083'
down_revision = '842cabcdb6f9'
branch_labels = None
depends_on = None


def upgrade():
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    existing_tables = inspector.get_table_names()
    if 'knowledge_documents' not in existing_tables:
        op.create_table(
            'knowledge_documents',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('title', sa.String(255), nullable=False),
            sa.Column('description', sa.String(500), nullable=True, server_default=''),
            sa.Column('content', sa.Text(), nullable=False),
            sa.Column('category', sa.String(100), nullable=True, server_default=''),
            sa.Column('priority', sa.Integer(), nullable=False, server_default='10'),
            sa.Column('is_active', sa.Boolean(), nullable=False, server_default='1'),
            sa.PrimaryKeyConstraint('id'),
        )


def downgrade():
    op.drop_table('knowledge_documents')
