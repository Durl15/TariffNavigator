"""add rate limiting

Revision ID: 005
Revises: 004
Create Date: 2024-02-19 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '005'
down_revision = '004'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ============================================================================
    # RATE_LIMITS TABLE (Sliding window rate limiting)
    # ============================================================================
    op.create_table(
        'rate_limits',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('identifier', sa.String(100), nullable=False),  # IP or user_id
        sa.Column('identifier_type', sa.String(10), nullable=False),  # 'ip' or 'user'
        sa.Column('request_count', sa.Integer(), nullable=False, server_default='1'),
        sa.Column('window_start', sa.DateTime(timezone=True), nullable=False),
        sa.Column('window_end', sa.DateTime(timezone=True), nullable=False),
        sa.Column('endpoint', sa.String(255), nullable=True),  # Optional: track per-endpoint
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
    )

    # Indexes for fast lookups
    op.create_index('ix_rate_limits_identifier', 'rate_limits', ['identifier'])
    op.create_index('ix_rate_limits_identifier_type', 'rate_limits', ['identifier_type'])
    op.create_index('ix_rate_limits_window_start', 'rate_limits', ['window_start'])

    # Composite index for rate limit checks (most critical for performance)
    op.create_index(
        'idx_rate_limit_lookup',
        'rate_limits',
        ['identifier', 'identifier_type', 'window_start']
    )

    # ============================================================================
    # ORGANIZATION_QUOTA_USAGE TABLE (Monthly calculation quotas)
    # ============================================================================
    op.create_table(
        'organization_quota_usage',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('organization_id', sa.String(36), nullable=False),
        sa.Column('year_month', sa.String(7), nullable=False),  # Format: "2024-03"
        sa.Column('calculation_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('quota_limit', sa.Integer(), nullable=False),  # Snapshot from Organization.max_calculations_per_month
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),

        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ondelete='CASCADE'),
    )

    # Unique index: one record per organization per month (SQLite compatible)
    op.create_index('idx_quota_lookup', 'organization_quota_usage', ['organization_id', 'year_month'], unique=True)

    # ============================================================================
    # RATE_LIMIT_VIOLATIONS TABLE (Log violations for analytics)
    # ============================================================================
    op.create_table(
        'rate_limit_violations',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('identifier', sa.String(100), nullable=False),
        sa.Column('identifier_type', sa.String(10), nullable=False),  # 'ip', 'user', 'organization'
        sa.Column('user_id', sa.String(36), nullable=True),
        sa.Column('violation_type', sa.String(20), nullable=False),  # 'ip_rate', 'user_rate', 'quota'
        sa.Column('attempted_count', sa.Integer(), nullable=False),
        sa.Column('limit', sa.Integer(), nullable=False),
        sa.Column('endpoint', sa.String(255), nullable=True),
        sa.Column('user_agent', sa.String(500), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),

        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='SET NULL'),
    )

    # Indexes for violation queries and analytics
    op.create_index('ix_rate_limit_violations_identifier', 'rate_limit_violations', ['identifier'])
    op.create_index('ix_rate_limit_violations_user_id', 'rate_limit_violations', ['user_id'])
    op.create_index('ix_rate_limit_violations_created_at', 'rate_limit_violations', ['created_at'])
    op.create_index('ix_rate_limit_violations_violation_type', 'rate_limit_violations', ['violation_type'])

    print("[+] Created rate limiting tables successfully")


def downgrade() -> None:
    # Drop tables in reverse order
    op.drop_table('rate_limit_violations')
    op.drop_table('organization_quota_usage')
    op.drop_table('rate_limits')

    print("[+] Dropped rate limiting tables successfully")
