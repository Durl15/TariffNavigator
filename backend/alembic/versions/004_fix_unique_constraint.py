"""fix unique constraint for code+country

Revision ID: 004
Revises: 003
Create Date: 2026-02-18 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect


# revision identifiers, used by Alembic.
revision = '004'
down_revision = '003'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Get connection to check existing indexes and constraints
    conn = op.get_bind()
    inspector = inspect(conn)
    existing_indexes = {idx['name']: idx for idx in inspector.get_indexes('hs_codes')}

    # Step 1: Drop foreign key constraints that reference hs_codes.code
    # This is necessary because we're about to make 'code' non-unique
    print("[*] Checking for foreign key constraints on hs_codes.code...")

    # Check if calculations table exists and has the FK
    try:
        fks = inspector.get_foreign_keys('calculations')
        for fk in fks:
            if fk.get('referred_table') == 'hs_codes' and 'code' in fk.get('referred_columns', []):
                fk_name = fk['name']
                print(f"[*] Dropping FK constraint {fk_name} from calculations")
                op.drop_constraint(fk_name, 'calculations', type_='foreignkey')
    except Exception as e:
        print(f"[*] No calculations FK to drop (table may not exist yet): {e}")

    # Check if catalog_items table exists and has the FK
    try:
        fks = inspector.get_foreign_keys('catalog_items')
        for fk in fks:
            if fk.get('referred_table') == 'hs_codes' and 'code' in fk.get('referred_columns', []):
                fk_name = fk['name']
                print(f"[*] Dropping FK constraint {fk_name} from catalog_items")
                op.drop_constraint(fk_name, 'catalog_items', type_='foreignkey')
    except Exception as e:
        print(f"[*] No catalog_items FK to drop (table may not exist yet): {e}")

    # Step 2: Create a new composite unique constraint on (code, country) first
    # This allows same code for different countries (e.g., 8517 for both CN and EU)
    if 'ix_hs_codes_code_country' not in existing_indexes:
        op.create_index('ix_hs_codes_code_country', 'hs_codes', ['code', 'country'], unique=True)
        print("[+] Created composite unique index on (code, country)")

    # Step 3: Handle the old unique index on code
    # If it exists and is unique, drop it and recreate as non-unique
    if 'ix_hs_codes_code' in existing_indexes:
        if existing_indexes['ix_hs_codes_code'].get('unique'):
            op.drop_index('ix_hs_codes_code', table_name='hs_codes')
            print("[+] Dropped unique index ix_hs_codes_code")
            op.create_index('ix_hs_codes_code', 'hs_codes', ['code'], unique=False)
            print("[+] Created non-unique index ix_hs_codes_code")
    else:
        # Index doesn't exist, create it as non-unique
        op.create_index('ix_hs_codes_code', 'hs_codes', ['code'], unique=False)
        print("[+] Created non-unique index ix_hs_codes_code")

    print("[+] Fixed: HS codes can now have same code for different countries")
    print("[!] Note: Foreign keys to hs_codes.code have been removed. Applications should lookup by (code, country).")


def downgrade() -> None:
    # Get connection to check existing indexes
    conn = op.get_bind()
    inspector = inspect(conn)
    existing_indexes = {idx['name']: idx for idx in inspector.get_indexes('hs_codes')}

    # Reverse the changes
    if 'ix_hs_codes_code' in existing_indexes:
        op.drop_index('ix_hs_codes_code', table_name='hs_codes')

    if 'ix_hs_codes_code_country' in existing_indexes:
        op.drop_index('ix_hs_codes_code_country', table_name='hs_codes')

    # Restore original unique index on code
    op.create_index('ix_hs_codes_code', 'hs_codes', ['code'], unique=True)

    # Note: We don't restore the foreign key constraints in downgrade
    # because they would need to be added in the migrations that created those tables
    print("[!] Note: Foreign key constraints were not restored. Add them manually if needed.")
