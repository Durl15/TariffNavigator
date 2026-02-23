# Database Configuration

## Current Setup: SQLite (Development)

**Database:** SQLite
**File:** `backend/tariffnavigator.db`
**Connection String:** `sqlite+aiosqlite:///./tariffnavigator.db`

### Why SQLite?

During development/testing on 2026-02-23, we discovered PostgreSQL was not installed on the development machine. SQLite provides a lightweight, zero-configuration alternative that works perfectly for development and testing.

### Configuration

**File:** `backend/.env` (not in git)

```bash
# SQLite (current - for local development)
DATABASE_URL=sqlite+aiosqlite:///./tariffnavigator.db

# PostgreSQL (production - requires PostgreSQL installed)
# DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/tariff_nav
```

**Default (in `backend/app/core/config.py`):**
```python
DATABASE_URL: str = "sqlite+aiosqlite:///./tariffnavigator.db"
```

### Switching to PostgreSQL (Production)

When deploying to production with PostgreSQL:

1. **Install PostgreSQL** (if not already installed)

2. **Create database:**
```bash
psql -U postgres
CREATE DATABASE tariff_nav;
```

3. **Update `.env` file:**
```bash
DATABASE_URL=postgresql+asyncpg://postgres:YOUR_PASSWORD@localhost:5432/tariff_nav
```

4. **Run migrations:**
```bash
cd backend
alembic upgrade head
```

### Database File Location

**SQLite database:** `backend/tariffnavigator.db` (544KB as of 2026-02-23)

**Note:** The SQLite database file is NOT in `.gitignore` but SHOULD be added if it contains sensitive data. For development, it contains test data only.

### Test Credentials

The SQLite database includes test users:

**Admin User:**
- Email: `admin@test.com`
- Password: `admin123`
- Role: admin

**Regular User:**
- Email: `test@test.com`
- Password: `password123`
- Role: user

### Migration Notes

**From PostgreSQL to SQLite (2026-02-23):**
- All existing data migrated successfully
- Test users verified working
- All endpoints functional with SQLite
- No code changes required (SQLAlchemy abstraction works perfectly)

### Performance Considerations

**SQLite is suitable for:**
- Development and testing ✅
- Small deployments (<100 concurrent users) ✅
- Read-heavy workloads ✅

**PostgreSQL recommended for:**
- Production deployments with high concurrency
- Multiple application servers
- Complex queries and analytics
- High write throughput

### Troubleshooting

**Issue:** Endpoints returning 500 errors
**Cause:** PostgreSQL configured but not running
**Solution:** Switch to SQLite or install/start PostgreSQL

**Issue:** Database locked errors
**Cause:** Multiple processes accessing SQLite concurrently
**Solution:** Use PostgreSQL for multi-process deployments

---

**Last Updated:** 2026-02-23
**Status:** SQLite working perfectly for development
