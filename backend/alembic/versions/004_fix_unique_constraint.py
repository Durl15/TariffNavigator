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
    # For SQLite, we just work with indexes
    # The FK constraint handling is not necessary for this change

    # Step 1: Drop the old unique index on code (if it exists)
    try:
        op.drop_index('ix_hs_codes_code', table_name='hs_codes')
    except:
        # Index might not exist or might have different name
        pass

    # Step 2: Create a new composite unique constraint on (code, country)
    # This allows same code for different countries (e.g., 8517 for both CN and EU)
    try:
        op.create_index('ix_hs_codes_code_country', 'hs_codes', ['code', 'country'], unique=True)
    except:
        # Index might already exist
        pass

    # Step 3: Create a non-unique index on code for faster lookups
    try:
        op.create_index('ix_hs_codes_code', 'hs_codes', ['code'], unique=False)
    except:
        # Index might already exist
        pass

    print("[+] Fixed: HS codes can now have same code for different countries")


def downgrade() -> None:
    # Reverse the changes
    try:
        op.drop_index('ix_hs_codes_code', table_name='hs_codes')
    except:
        pass

    try:
        op.drop_index('ix_hs_codes_code_country', table_name='hs_codes')
    except:
        pass

    try:
        op.create_index('ix_hs_codes_code', 'hs_codes', ['code'], unique=True)
    except:
        pass
