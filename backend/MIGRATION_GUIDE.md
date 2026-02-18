# Database Migration Guide

This guide will help you migrate from SQLite to PostgreSQL and set up the new enterprise tables.

## Prerequisites

1. **PostgreSQL 15+** installed (locally or cloud)
2. **Python dependencies** updated
3. **Backup** of existing SQLite database

---

## Step 1: Install Missing Dependencies

```bash
cd backend

# Add to requirements.txt
cat >> requirements.txt << EOF
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
aiosqlite==0.20.0
EOF

# Install
pip install -r requirements.txt
```

---

## Step 2: Set Up PostgreSQL

### Option A: Local Docker (Easiest for development)

```bash
# Start PostgreSQL container
docker run --name tariff-postgres \
  -e POSTGRES_USER=tariffnav \
  -e POSTGRES_PASSWORD=dev123 \
  -e POSTGRES_DB=tariffnav \
  -p 5432:5432 \
  -d postgres:15

# Verify it's running
docker ps
```

### Option B: Railway.app (Free cloud option)

1. Go to [railway.app](https://railway.app)
2. Sign up with GitHub
3. Click "New Project" → "Provision PostgreSQL"
4. Copy the connection string

### Option C: AWS RDS (Production)

1. Go to AWS Console → RDS
2. Create database → PostgreSQL 15
3. Instance: db.t3.micro (free tier eligible)
4. Enable automatic backups
5. Copy the endpoint URL

---

## Step 3: Update Environment Variables

```bash
# Backup old .env
cp .env .env.backup

# Edit .env
nano .env
```

Update the following:

```bash
# OLD (SQLite)
# DATABASE_URL=sqlite+aiosqlite:///./tariffnavigator.db

# NEW (PostgreSQL)
DATABASE_URL=postgresql+asyncpg://tariffnav:dev123@localhost:5432/tariffnav

# For Railway/AWS, use their provided URL:
# DATABASE_URL=postgresql+asyncpg://user:pass@host:port/dbname

# Generate a secure secret key (run: python -c "import secrets; print(secrets.token_urlsafe(32))")
SECRET_KEY=your-generated-secure-key-here

# Optional: OpenAI for AI classification
OPENAI_API_KEY=sk-your-key-here
```

---

## Step 4: Migrate Existing Data (Optional)

If you have existing HS codes in SQLite that you want to migrate:

```bash
# Export from SQLite
sqlite3 tariffnavigator.db << EOF
.headers on
.mode csv
.output hs_codes_export.csv
SELECT code, description, level, country, mfn_rate, general_rate, vat_rate, consumption_tax, unit, fta_rate, fta_name, fta_countries FROM hs_codes;
.quit
EOF

# Create Python script to import
python << 'SCRIPT'
import asyncio
import csv
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import async_session
from app.models.hs_code import HSCode

async def import_hs_codes():
    async with async_session() as db:
        with open('hs_codes_export.csv', 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                code = HSCode(
                    code=row['code'],
                    description=row['description'],
                    level=row['level'],
                    country=row['country'],
                    mfn_rate=float(row['mfn_rate']) if row['mfn_rate'] else 0,
                    general_rate=float(row['general_rate']) if row['general_rate'] else 0,
                    vat_rate=float(row['vat_rate']) if row['vat_rate'] else 0,
                    consumption_tax=float(row['consumption_tax']) if row['consumption_tax'] else 0,
                    unit=row['unit'],
                    fta_rate=float(row['fta_rate']) if row['fta_rate'] else None,
                    fta_name=row['fta_name'] if row['fta_name'] else None,
                    fta_countries=row['fta_countries'] if row['fta_countries'] else None,
                )
                db.add(code)

        await db.commit()
        print("✅ Imported HS codes successfully")

asyncio.run(import_hs_codes())
SCRIPT
```

---

## Step 5: Run Migrations

```bash
# Check current migration status
alembic current

# Should show: 002 (head)

# Run the new migration
alembic upgrade head

# You should see:
# INFO  [alembic.runtime.migration] Running upgrade 002 -> 003, create users and enterprise tables
# ✅ Created users and enterprise tables successfully
```

---

## Step 6: Create Admin User

```bash
# Run the admin creation script
python scripts/create_admin_user.py

# Follow the prompts:
# Admin Email: admin@yourcompany.com
# Full Name: Admin User
# Password: ********
# Confirm Password: ********

# You should see:
# ✅ Admin user created successfully!
```

---

## Step 7: Verify Migration

```bash
# Start the server
uvicorn main:app --reload

# In another terminal, test the API
curl http://localhost:8000/api/v1/health

# Test login
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@yourcompany.com",
    "password": "your-password"
  }'

# Should return:
# {
#   "access_token": "eyJ...",
#   "token_type": "bearer"
# }
```

---

## Step 8: Seed More HS Codes (Optional)

```bash
# Run the existing seed script
python scripts/seed_cn_eu_fixed.py

# Or create your own import script for full USITC/TARIC databases
```

---

## Rollback (if needed)

If something goes wrong:

```bash
# Rollback to previous migration
alembic downgrade 002

# Switch back to SQLite
# Edit .env: DATABASE_URL=sqlite+aiosqlite:///./tariffnavigator.db

# Restart server
```

---

## Database Schema Overview

After migration, you'll have these tables:

### Core Tables
- **organizations** - Multi-tenant support
- **users** - User accounts with roles
- **hs_codes** - HS code database (existing)

### Feature Tables
- **calculations** - Saved user calculations
- **shared_links** - Shareable calculation links
- **audit_logs** - Activity tracking
- **api_keys** - API access for integrations
- **saved_filters** - User search preferences
- **notifications** - In-app notifications

---

## Troubleshooting

### "Relation already exists" error
```bash
# Drop all tables and start fresh
alembic downgrade base
alembic upgrade head
```

### Connection refused (PostgreSQL)
```bash
# Check if PostgreSQL is running
docker ps  # For Docker
# OR
pg_isready -h localhost -p 5432  # For native install
```

### "Module not found" errors
```bash
# Make sure you're in the right directory
cd backend
# Reinstall dependencies
pip install -r requirements.txt
```

### Import errors in migration
```bash
# Check that all model files exist
ls -la app/models/

# Expected files:
# - __init__.py
# - user.py
# - organization.py
# - calculation.py
# - hs_code.py
```

---

## Next Steps

1. ✅ Update your API endpoints to use the new models
2. ✅ Implement the calculations save/list endpoints
3. ✅ Add share link generation
4. ✅ Set up audit logging middleware
5. ✅ Deploy to production with proper connection pooling

---

## Production Checklist

Before deploying:

- [ ] Use a strong SECRET_KEY (not the default)
- [ ] Enable SSL/TLS for database connections
- [ ] Set up automated backups
- [ ] Configure connection pooling
- [ ] Set up monitoring (Sentry, DataDog)
- [ ] Use a managed PostgreSQL service (RDS, Cloud SQL)
- [ ] Enable point-in-time recovery
- [ ] Set up read replicas for scaling
- [ ] Configure proper CORS origins (not "*")
- [ ] Add rate limiting
- [ ] Set up log aggregation

---

## Support

If you encounter issues:
1. Check the logs: `docker logs tariff-postgres` (for Docker)
2. Verify migrations: `alembic current`
3. Check database connection: `psql` or `pgcli`
4. Review error messages carefully

---

🎉 **You're all set!** Your database is now ready for enterprise features.
