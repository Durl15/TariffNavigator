"""Add tool_analyses table

Revision ID: 009
Revises: 008
Create Date: 2026-03-08
"""
from alembic import op
import sqlalchemy as sa

revision = '009'
down_revision = '008'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'tool_analyses',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('user_id', sa.String(36), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('tool_type', sa.String(50), nullable=False, index=True),
        sa.Column('title', sa.String(255), nullable=False),
        sa.Column('form_data', sa.JSON, nullable=True),
        sa.Column('result_data', sa.JSON, nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, index=True),
    )
    op.create_index('idx_tool_analyses_user_type', 'tool_analyses', ['user_id', 'tool_type'])


def downgrade() -> None:
    op.drop_index('idx_tool_analyses_user_type', 'tool_analyses')
    op.drop_table('tool_analyses')
