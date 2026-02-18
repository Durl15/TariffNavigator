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
    # Step 1: Drop the foreign key constraint that depends on the index
    # This FK prevents the same HS code from existing in multiple countries
    op.drop_constraint('calculations_hs_code_fkey', 'calculations', type_='foreignkey')

    # Step 2: Drop the old unique index on code
    op.drop_index('ix_hs_codes_code', table_name='hs_codes')

    # Step 3: Create a new composite unique constraint on (code, country)
    # This allows same code for different countries (e.g., 8517 for both CN and EU)
    op.create_index('ix_hs_codes_code_country', 'hs_codes', ['code', 'country'], unique=True)

    # Step 4: Create a non-unique index on code for faster lookups
    op.create_index('ix_hs_codes_code', 'hs_codes', ['code'], unique=False)

    # Note: We don't recreate the foreign key because it would need to reference
    # both code AND country, but calculations table only has hs_code column.
    # The application validates HS codes exist before saving calculations.

    print("✅ Fixed: HS codes can now have same code for different countries")


def downgrade() -> None:
    # Reverse the changes
    op.drop_index('ix_hs_codes_code', table_name='hs_codes')
    op.drop_index('ix_hs_codes_code_country', table_name='hs_codes')
    op.create_index('ix_hs_codes_code', 'hs_codes', ['code'], unique=True)

    # Recreate the foreign key constraint
    op.create_foreign_key(
        'calculations_hs_code_fkey',
        'calculations',
        'hs_codes',
        ['hs_code'],
        ['code']
    )
