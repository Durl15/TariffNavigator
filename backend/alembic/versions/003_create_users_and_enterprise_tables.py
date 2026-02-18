"""create users and enterprise tables

Revision ID: 003
Revises: 002
Create Date: 2024-02-16 14:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '003'
down_revision = '002'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ============================================================================
    # ORGANIZATIONS TABLE (Multi-tenant support)
    # ============================================================================
    op.create_table(
        'organizations',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('slug', sa.String(100), nullable=False, unique=True),
        sa.Column('plan', sa.String(50), nullable=False, server_default='free'),
        sa.Column('status', sa.String(50), nullable=False, server_default='active'),
        sa.Column('max_users', sa.Integer(), nullable=False, server_default='5'),
        sa.Column('max_calculations_per_month', sa.Integer(), nullable=False, server_default='100'),
        sa.Column('settings', sa.JSON(), nullable=True),  # Custom org settings
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),  # Soft delete
    )
    op.create_index('ix_organizations_slug', 'organizations', ['slug'])
    op.create_index('ix_organizations_plan', 'organizations', ['plan'])
    op.create_index('ix_organizations_status', 'organizations', ['status'])

    # ============================================================================
    # USERS TABLE
    # ============================================================================
    op.create_table(
        'users',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('email', sa.String(255), nullable=False, unique=True),
        sa.Column('hashed_password', sa.String(255), nullable=False),
        sa.Column('full_name', sa.String(255), nullable=True),
        sa.Column('role', sa.String(50), nullable=False, server_default='user'),
        sa.Column('organization_id', sa.String(36), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('is_superuser', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('is_email_verified', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('email_verification_token', sa.String(255), nullable=True),
        sa.Column('password_reset_token', sa.String(255), nullable=True),
        sa.Column('password_reset_expires', sa.DateTime(timezone=True), nullable=True),
        sa.Column('last_login_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('login_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('preferences', sa.JSON(), nullable=True),  # User preferences (theme, default currency, etc.)
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),  # Soft delete
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ondelete='SET NULL'),
    )
    op.create_index('ix_users_email', 'users', ['email'])
    op.create_index('ix_users_organization_id', 'users', ['organization_id'])
    op.create_index('ix_users_role', 'users', ['role'])
    op.create_index('ix_users_is_active', 'users', ['is_active'])
    op.create_index('ix_users_email_verification_token', 'users', ['email_verification_token'])
    op.create_index('ix_users_password_reset_token', 'users', ['password_reset_token'])

    # ============================================================================
    # CALCULATIONS TABLE (Save user calculations)
    # ============================================================================
    op.create_table(
        'calculations',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('user_id', sa.String(36), nullable=False),
        sa.Column('organization_id', sa.String(36), nullable=True),
        sa.Column('name', sa.String(255), nullable=True),  # User-given name
        sa.Column('description', sa.Text(), nullable=True),

        # Input data
        sa.Column('hs_code', sa.String(20), nullable=False),
        sa.Column('product_description', sa.Text(), nullable=True),
        sa.Column('origin_country', sa.String(2), nullable=False),
        sa.Column('destination_country', sa.String(2), nullable=False),
        sa.Column('cif_value', sa.Numeric(12, 2), nullable=False),
        sa.Column('currency', sa.String(3), nullable=False, server_default='USD'),

        # Results (stored as JSON for flexibility)
        sa.Column('result', sa.JSON(), nullable=False),  # Full calculation result
        sa.Column('total_cost', sa.Numeric(12, 2), nullable=False),
        sa.Column('customs_duty', sa.Numeric(12, 2), nullable=True),
        sa.Column('vat_amount', sa.Numeric(12, 2), nullable=True),
        sa.Column('fta_eligible', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('fta_savings', sa.Numeric(12, 2), nullable=True),

        # Metadata
        sa.Column('is_favorite', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('tags', sa.JSON(), nullable=True),  # Array of tags
        sa.Column('view_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),  # Soft delete

        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['hs_code'], ['hs_codes.code'], ondelete='SET NULL'),
    )
    op.create_index('ix_calculations_user_id', 'calculations', ['user_id'])
    op.create_index('ix_calculations_organization_id', 'calculations', ['organization_id'])
    op.create_index('ix_calculations_hs_code', 'calculations', ['hs_code'])
    op.create_index('ix_calculations_created_at', 'calculations', ['created_at'])
    op.create_index('ix_calculations_user_created', 'calculations', ['user_id', 'created_at'])
    op.create_index('ix_calculations_is_favorite', 'calculations', ['user_id', 'is_favorite'])

    # ============================================================================
    # SHARED_LINKS TABLE (Shareable calculation links)
    # ============================================================================
    op.create_table(
        'shared_links',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('token', sa.String(100), nullable=False, unique=True),
        sa.Column('calculation_id', sa.String(36), nullable=False),
        sa.Column('created_by_user_id', sa.String(36), nullable=False),
        sa.Column('access_level', sa.String(20), nullable=False, server_default='view'),
        sa.Column('password_hash', sa.String(255), nullable=True),  # Optional password protection
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('view_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('last_accessed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),

        sa.ForeignKeyConstraint(['calculation_id'], ['calculations.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['created_by_user_id'], ['users.id'], ondelete='CASCADE'),
    )
    op.create_index('ix_shared_links_token', 'shared_links', ['token'])
    op.create_index('ix_shared_links_calculation_id', 'shared_links', ['calculation_id'])
    op.create_index('ix_shared_links_is_active', 'shared_links', ['is_active'])

    # ============================================================================
    # AUDIT_LOGS TABLE (Track all user actions)
    # ============================================================================
    op.create_table(
        'audit_logs',
        sa.Column('id', sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column('user_id', sa.String(36), nullable=True),
        sa.Column('organization_id', sa.String(36), nullable=True),
        sa.Column('action', sa.String(50), nullable=False),
        sa.Column('resource_type', sa.String(50), nullable=False),
        sa.Column('resource_id', sa.String(36), nullable=True),
        sa.Column('changes', sa.JSON(), nullable=True),  # Before/after values
        sa.Column('ip_address', sa.String(45), nullable=True),  # IPv6 compatible
        sa.Column('user_agent', sa.Text(), nullable=True),
        sa.Column('endpoint', sa.String(255), nullable=True),
        sa.Column('method', sa.String(10), nullable=True),  # GET, POST, etc.
        sa.Column('status_code', sa.Integer(), nullable=True),
        sa.Column('duration_ms', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),

        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ondelete='SET NULL'),
    )
    op.create_index('ix_audit_logs_user_id', 'audit_logs', ['user_id'])
    op.create_index('ix_audit_logs_organization_id', 'audit_logs', ['organization_id'])
    op.create_index('ix_audit_logs_action', 'audit_logs', ['action'])
    op.create_index('ix_audit_logs_resource', 'audit_logs', ['resource_type', 'resource_id'])
    op.create_index('ix_audit_logs_created_at', 'audit_logs', ['created_at'])

    # ============================================================================
    # API_KEYS TABLE (For programmatic access)
    # ============================================================================
    op.create_table(
        'api_keys',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('user_id', sa.String(36), nullable=False),
        sa.Column('organization_id', sa.String(36), nullable=True),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('key_prefix', sa.String(20), nullable=False),  # First 8 chars (for display)
        sa.Column('key_hash', sa.String(255), nullable=False),  # Hashed full key
        sa.Column('scopes', sa.JSON(), nullable=True),  # Array of allowed scopes
        sa.Column('rate_limit', sa.Integer(), nullable=False, server_default='100'),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('last_used_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('usage_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('revoked_at', sa.DateTime(timezone=True), nullable=True),

        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ondelete='CASCADE'),
    )
    op.create_index('ix_api_keys_key_hash', 'api_keys', ['key_hash'])
    op.create_index('ix_api_keys_user_id', 'api_keys', ['user_id'])
    op.create_index('ix_api_keys_is_active', 'api_keys', ['is_active'])

    # ============================================================================
    # SAVED_FILTERS TABLE (User preferences for searches)
    # ============================================================================
    op.create_table(
        'saved_filters',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('user_id', sa.String(36), nullable=False),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('filter_json', sa.JSON(), nullable=False),
        sa.Column('is_default', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),

        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
    )
    op.create_index('ix_saved_filters_user_id', 'saved_filters', ['user_id'])

    # ============================================================================
    # NOTIFICATIONS TABLE (In-app notifications)
    # ============================================================================
    op.create_table(
        'notifications',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('user_id', sa.String(36), nullable=False),
        sa.Column('type', sa.String(50), nullable=False),
        sa.Column('title', sa.String(255), nullable=False),
        sa.Column('message', sa.Text(), nullable=True),
        sa.Column('link', sa.String(255), nullable=True),
        sa.Column('data', sa.JSON(), nullable=True),  # Additional structured data
        sa.Column('is_read', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('read_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),

        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
    )
    op.create_index('ix_notifications_user_id', 'notifications', ['user_id'])
    op.create_index('ix_notifications_user_read', 'notifications', ['user_id', 'is_read'])
    op.create_index('ix_notifications_created_at', 'notifications', ['created_at'])

    # ============================================================================
    # Insert default organization for existing users (if any)
    # ============================================================================
    op.execute("""
        INSERT INTO organizations (id, name, slug, plan, status)
        VALUES (
            '00000000-0000-0000-0000-000000000001',
            'Default Organization',
            'default',
            'free',
            'active'
        )
    """)

    print("[+] Created users and enterprise tables successfully")


def downgrade() -> None:
    # Drop tables in reverse order (respecting foreign keys)
    op.drop_table('notifications')
    op.drop_table('saved_filters')
    op.drop_table('api_keys')
    op.drop_table('audit_logs')
    op.drop_table('shared_links')
    op.drop_table('calculations')
    op.drop_table('users')
    op.drop_table('organizations')

    print("[+] Dropped users and enterprise tables successfully")
