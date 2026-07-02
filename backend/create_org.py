# Create organization and assign user
# Just run: python create_org.py

import uuid
from sqlalchemy import create_engine, text

# Step 1: Production database connection
DATABASE_URL = 'postgresql://tariffnavigator:REDACTED_DB_PASSWORD@dpg-d6a8l7h4tr6s73d48dd0-a.oregon-postgres.render.com/tariffnavigator'

# Step 2: User email
EMAIL = 'admin@test.com'

# Step 3: Connect to database
print('Connecting to database...')
engine = create_engine(DATABASE_URL)

with engine.begin() as conn:
    # Step 4: Get user ID
    print('Finding user...')
    result = conn.execute(
        text("SELECT id FROM users WHERE email = :email"),
        {'email': EMAIL}
    )
    user_row = result.fetchone()

    if not user_row:
        print('❌ ERROR: User not found!')
        exit(1)

    user_id = user_row[0]
    print(f'Found user: {user_id}')

    # Step 5: Create organization
    print('Creating organization...')
    org_id = str(uuid.uuid4())

    conn.execute(
        text("""
            INSERT INTO organizations (id, name, slug, plan, status, created_at, updated_at)
            VALUES (:id, :name, :slug, :plan, 'active', NOW(), NOW())
            ON CONFLICT (slug) DO NOTHING
        """),
        {
            'id': org_id,
            'name': 'Admin Organization',
            'slug': 'admin-org',
            'plan': 'pro'
        }
    )
    print(f'Created organization: {org_id}')

    # Step 6: Assign user to organization
    print('Assigning user to organization...')
    conn.execute(
        text("UPDATE users SET organization_id = :org_id WHERE id = :user_id"),
        {'org_id': org_id, 'user_id': user_id}
    )

    print('')
    print('✅ SUCCESS! Organization created and user assigned!')
    print('')
    print('Organization Details:')
    print(f'  Name: Admin Organization')
    print(f'  Plan: Pro')
    print(f'  ID: {org_id}')
    print('')
    print('Features unlocked:')
    print('  ✅ Watchlists (up to 10)')
    print('  ✅ Advanced catalogs')
    print('  ✅ API access')
    print('')
    print('Logout and login again, then try creating a watchlist!')
