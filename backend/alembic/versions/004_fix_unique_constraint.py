"""fix unique constraint for code+country

Revision ID: 004
Revises: 003
Create Date: 2026-02-18 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '004'
down_revision = '003'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Drop the old unique index on code
    op.drop_index('ix_hs_codes_code', table_name='hs_codes')

    # Create a new composite unique constraint on (code, country)
    op.create_index('ix_hs_codes_code_country', 'hs_codes', ['code', 'country'], unique=True)

    # Also create a non-unique index on code for faster lookups
    op.create_index('ix_hs_codes_code', 'hs_codes', ['code'], unique=False)

    print("✅ Fixed: HS codes can now have same code for different countries")


def downgrade() -> None:
    # Reverse the changes
    op.drop_index('ix_hs_codes_code', table_name='hs_codes')
    op.drop_index('ix_hs_codes_code_country', table_name='hs_codes')
    op.create_index('ix_hs_codes_code', 'hs_codes', ['code'], unique=True)
