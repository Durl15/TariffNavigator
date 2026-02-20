"""create watchlist and alert tables

Revision ID: 007
Revises: 006
Create Date: 2026-02-20 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '007'
down_revision = '006'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ============================================================================
    # WATCHLISTS TABLE (User-defined tariff watchlists)
    # ============================================================================
    op.create_table(
        'watchlists',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('user_id', sa.String(36), nullable=False),

        # Metadata
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),

        # Watch criteria (JSON arrays for flexibility)
        sa.Column('hs_codes', sa.JSON(), nullable=True),  # ["8703.23", "8471.30"]
        sa.Column('countries', sa.JSON(), nullable=True),  # ["CN", "MX", "CA"]

        # Alert preferences
        sa.Column('alert_preferences', sa.JSON(), nullable=True),  # {email: true, digest: 'daily'}

        # Status
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),

        # Timestamps
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),

        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
    )

    # Indexes for fast lookups
    op.create_index('ix_watchlists_user_id', 'watchlists', ['user_id'])
    op.create_index('ix_watchlists_is_active', 'watchlists', ['is_active'])
    op.create_index('ix_watchlists_created_at', 'watchlists', ['created_at'])

    # ============================================================================
    # TARIFF_CHANGE_LOGS TABLE (Track tariff rate changes)
    # ============================================================================
    op.create_table(
        'tariff_change_logs',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),

        # Change classification
        sa.Column('change_type', sa.String(50), nullable=False),  # 'rate_update', 'new_program', 'expiration'

        # What changed
        sa.Column('hs_code', sa.String(20), nullable=True),
        sa.Column('country', sa.String(2), nullable=True),

        # Change values (JSON for flexibility)
        sa.Column('old_value', sa.JSON(), nullable=True),
        sa.Column('new_value', sa.JSON(), nullable=True),

        # Metadata
        sa.Column('source', sa.String(100), nullable=True),  # 'internal', 'federal_register', 'cbp'
        sa.Column('detected_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),

        # Notification tracking
        sa.Column('notifications_sent', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('notification_count', sa.Integer(), nullable=False, server_default='0'),
    )

    # Indexes for change detection and querying
    op.create_index('ix_tariff_change_logs_change_type', 'tariff_change_logs', ['change_type'])
    op.create_index('ix_tariff_change_logs_hs_code', 'tariff_change_logs', ['hs_code'])
    op.create_index('ix_tariff_change_logs_country', 'tariff_change_logs', ['country'])
    op.create_index('ix_tariff_change_logs_detected_at', 'tariff_change_logs', ['detected_at'])
    op.create_index('ix_tariff_change_logs_notifications_sent', 'tariff_change_logs', ['notifications_sent'])
    op.create_index('idx_tariff_change_logs_hs_country', 'tariff_change_logs', ['hs_code', 'country'])

    print("[+] Created watchlist and alert tables successfully")


def downgrade() -> None:
    # Drop tables in reverse order
    op.drop_table('tariff_change_logs')
    op.drop_table('watchlists')

    print("[+] Dropped watchlist and alert tables successfully")
