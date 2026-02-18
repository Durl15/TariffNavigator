# Quick Start Guide - Database Migration

This is the **5-minute quick start** to get your new database schema up and running.

## 🚀 Quick Steps

### 1. Install Dependencies (1 minute)

```bash
cd backend
pip install -r requirements.txt
```

### 2. Start PostgreSQL (1 minute)

**Easiest Option - Docker:**
```bash
docker run --name tariff-postgres \
  -e POSTGRES_USER=tariffnav \
  -e POSTGRES_PASSWORD=dev123 \
  -e POSTGRES_DB=tariffnav \
  -p 5432:5432 \
  -d postgres:15
```

### 3. Update .env (30 seconds)

```bash
# Edit backend/.env
nano .env
```

Change this line:
```bash
DATABASE_URL=postgresql+asyncpg://tariffnav:dev123@localhost:5432/tariffnav
```

### 4. Run Migration (30 seconds)

```bash
alembic upgrade head
```

You should see:
```
INFO  [alembic.runtime.migration] Running upgrade 002 -> 003
✅ Created users and enterprise tables successfully
```

### 5. Create Admin User (1 minute)

```bash
python scripts/create_admin_user.py
```

Enter:
- Email: `admin@test.com`
- Name: `Admin User`
- Password: `admin123` (change in production!)

### 6. Test It (30 seconds)

```bash
# Start server
uvicorn main:app --reload

# In another terminal, test login
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "admin@test.com", "password": "admin123"}'
```

You should get:
```json
{
  "access_token": "eyJ...",
  "token_type": "bearer"
}
```

## ✅ Done!

You now have:
- ✅ PostgreSQL database running
- ✅ 8 new tables created (users, organizations, calculations, etc.)
- ✅ Admin user ready to log in
- ✅ Ready to build enterprise features

## 📋 What Changed?

**New Tables:**
1. `organizations` - Multi-tenant support
2. `users` - Enhanced user management
3. `calculations` - Save user calculations
4. `shared_links` - Shareable calculation URLs
5. `audit_logs` - Track all user actions
6. `api_keys` - API access tokens
7. `saved_filters` - User search preferences
8. `notifications` - In-app notifications

**Enhanced `hs_codes` table:**
- Added FTA columns (already migrated in 002)

## 🔥 Hot Tips

**View Tables:**
```bash
# Connect to database
docker exec -it tariff-postgres psql -U tariffnav -d tariffnav

# List tables
\dt

# Describe users table
\d users

# Exit
\q
```

**Reset Database (if needed):**
```bash
alembic downgrade base
alembic upgrade head
python scripts/create_admin_user.py
```

**Stop PostgreSQL:**
```bash
docker stop tariff-postgres
docker rm tariff-postgres
```

## 🆘 Troubleshooting

**"Connection refused"**
```bash
# Check Docker is running
docker ps

# Restart PostgreSQL
docker restart tariff-postgres
```

**"Module not found: jose"**
```bash
# Reinstall dependencies
pip install -r requirements.txt
```

**"Relation already exists"**
```bash
# Drop and recreate
alembic downgrade base
alembic upgrade head
```

---

## Next Steps

Now that your database is set up:

1. **Update API endpoints** to save calculations
2. **Implement share links** feature
3. **Add audit logging** middleware
4. **Build admin panel** in frontend

See `MIGRATION_GUIDE.md` for detailed production deployment steps.

---

🎉 **Happy Coding!**
