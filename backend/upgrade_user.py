# Upgrade user to Pro tier
# Just run: python upgrade_user.py

from sqlalchemy import create_engine, text

# Step 1: Production database connection
DATABASE_URL = 'postgresql://tariffnavigator:REDACTED_DB_PASSWORD@dpg-d6a8l7h4tr6s73d48dd0-a.oregon-postgres.render.com/tariffnavigator'

# Step 2: User to upgrade
EMAIL = 'admin@test.com'

# Step 3: Connect to database
print('Connecting to database...')
engine = create_engine(DATABASE_URL)

# Step 4: Upgrade user to Pro tier
print('Upgrading user to Pro tier...')
with engine.begin() as conn:
    result = conn.execute(
        text("UPDATE users SET role = 'pro' WHERE email = :email"),
        {'email': EMAIL}
    )

    if result.rowcount == 0:
        print('❌ ERROR: User not found!')
    else:
        print('')
        print('✅ SUCCESS! User upgraded to Pro!')
        print('')
        print('Features unlocked:')
        print('  ✅ Watchlists (up to 10)')
        print('  ✅ Advanced notifications')
        print('  ✅ API access')
        print('  ✅ All countries')
        print('')
        print('Refresh the page and try creating a watchlist!')
