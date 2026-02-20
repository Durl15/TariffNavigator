"""add catalog models

Revision ID: 006
Revises: 005
Create Date: 2026-02-19 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '006'
down_revision = '005'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ============================================================================
    # CATALOGS TABLE (Product catalogs uploaded by users)
    # ============================================================================
    op.create_table(
        'catalogs',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('user_id', sa.String(36), nullable=False),
        sa.Column('organization_id', sa.String(36), nullable=True),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('currency', sa.String(3), nullable=False, server_default='USD'),
        sa.Column('total_skus', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('uploaded_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),

        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ondelete='SET NULL'),
    )

    # Indexes for fast lookups
    op.create_index('ix_catalogs_user_id', 'catalogs', ['user_id'])
    op.create_index('ix_catalogs_organization_id', 'catalogs', ['organization_id'])
    op.create_index('ix_catalogs_created_at', 'catalogs', ['created_at'])

    # ============================================================================
    # CATALOG_ITEMS TABLE (Individual products in catalog)
    # ============================================================================
    op.create_table(
        'catalog_items',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('catalog_id', sa.String(36), nullable=False),
        sa.Column('sku', sa.String(100), nullable=False),
        sa.Column('product_name', sa.String(255), nullable=True),
        sa.Column('hs_code', sa.String(20), nullable=True),
        sa.Column('origin_country', sa.String(2), nullable=False),
        sa.Column('cogs', sa.Numeric(12, 2), nullable=False),
        sa.Column('retail_price', sa.Numeric(12, 2), nullable=False),
        sa.Column('annual_volume', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('category', sa.String(100), nullable=True),
        sa.Column('weight_kg', sa.Numeric(10, 2), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),

        # Calculated fields (cached for performance)
        sa.Column('tariff_cost', sa.Numeric(12, 2), nullable=True),
        sa.Column('landed_cost', sa.Numeric(12, 2), nullable=True),
        sa.Column('gross_margin', sa.Numeric(12, 2), nullable=True),
        sa.Column('margin_percent', sa.Numeric(5, 2), nullable=True),
        sa.Column('annual_tariff_exposure', sa.Numeric(12, 2), nullable=True),

        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),

        sa.ForeignKeyConstraint(['catalog_id'], ['catalogs.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['hs_code'], ['hs_codes.code'], ondelete='SET NULL'),
    )

    # Indexes for fast lookups and queries
    op.create_index('ix_catalog_items_catalog_id', 'catalog_items', ['catalog_id'])
    op.create_index('ix_catalog_items_hs_code', 'catalog_items', ['hs_code'])
    op.create_index('ix_catalog_items_category', 'catalog_items', ['category'])
    op.create_index('idx_catalog_items_sku', 'catalog_items', ['catalog_id', 'sku'])

    print("[+] Created catalog tables successfully")


def downgrade() -> None:
    # Drop tables in reverse order
    op.drop_table('catalog_items')
    op.drop_table('catalogs')

    print("[+] Dropped catalog tables successfully")
