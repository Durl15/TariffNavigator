"""add_fta_columns

Revision ID: 002
Revises: 001
Create Date: 2026-02-16 15:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


revision = '002'
down_revision = '001'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('hs_codes', sa.Column('fta_rate', sa.Float(), nullable=True))
    op.add_column('hs_codes', sa.Column('fta_name', sa.String(length=100), nullable=True))
    op.add_column('hs_codes', sa.Column('fta_countries', sa.String(length=200), nullable=True))


def downgrade() -> None:
    op.drop_column('hs_codes', 'fta_countries')
    op.drop_column('hs_codes', 'fta_name')
    op.drop_column('hs_codes', 'fta_rate')