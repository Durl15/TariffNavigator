# Quick Test Guide - Admin Panel

## 5-Minute Test Run

### Step 1: Start Server (30 seconds)
```bash
cd backend
uvicorn main:app --reload
```

### Step 2: Create Admin (1 minute)
```bash
python scripts/create_admin_user.py
```
- Email: `admin@test.com`
- Password: `admin123`

### Step 3: Get Token (30 seconds)
```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "admin@test.com", "password": "admin123"}'
```

Save the `access_token` from the response.

### Step 4: Test Endpoints (3 minutes)

Replace `YOUR_TOKEN` with the token from Step 3.

#### Test 1: System Stats
```bash
curl -H "Authorization: Bearer YOUR_TOKEN" \
  http://localhost:8000/api/v1/admin/stats
```

**Expected:** System statistics (user counts, calculations, etc.)

#### Test 2: List Users
```bash
curl -H "Authorization: Bearer YOUR_TOKEN" \
  http://localhost:8000/api/v1/admin/users
```

**Expected:** Paginated user list with at least your admin user

#### Test 3: Create User
```bash
curl -X POST \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "test123456",
    "full_name": "Test User",
    "role": "user"
  }' \
  http://localhost:8000/api/v1/admin/users
```

**Expected:** 201 Created with new user details

#### Test 4: List Organizations
```bash
curl -H "Authorization: Bearer YOUR_TOKEN" \
  http://localhost:8000/api/v1/admin/organizations
```

**Expected:** List of organizations (at least the default one)

#### Test 5: Audit Logs
```bash
curl -H "Authorization: Bearer YOUR_TOKEN" \
  http://localhost:8000/api/v1/admin/audit-logs
```

**Expected:** Audit log entries showing the user creation from Test 3

---

## All 14 Endpoints at a Glance

### User Management (7)
```
GET    /admin/users                    - List users
POST   /admin/users                    - Create user
GET    /admin/users/{id}               - Get user
PUT    /admin/users/{id}               - Update user
DELETE /admin/users/{id}               - Delete user
POST   /admin/users/bulk-action        - Bulk operations
```

### Organization Management (3)
```
GET    /admin/organizations            - List orgs
POST   /admin/organizations            - Create org
PUT    /admin/organizations/{id}       - Update org
```

### Audit & Stats (4)
```
GET    /admin/audit-logs               - List audit logs
GET    /admin/stats                    - System stats
GET    /admin/stats/activity           - Activity over time
GET    /admin/stats/popular-hs-codes   - Popular codes
```

---

## Common Issues

### 401 Unauthorized
- Check token is included in Authorization header
- Verify token format: `Bearer YOUR_TOKEN`
- Token may have expired, login again

### 403 Forbidden
- User doesn't have admin/superuser role
- Check user's role in database
- Use the admin user created in Step 2

### 404 Not Found
- Check URL is correct
- Ensure server is running
- Verify `/admin` prefix is included

### 500 Internal Server Error
- Check server logs
- Verify database is running
- Ensure migrations are up to date

---

## API Documentation

Once server is running, visit:
- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

All admin endpoints will be documented under the "admin" tag.

---

## What's Working

✓ All 14 admin endpoints
✓ JWT authentication
✓ Role-based access control
✓ Audit logging middleware
✓ Request validation
✓ Error handling
✓ Pagination
✓ Search and filtering

---

## Production Checklist

Before deploying to production:

1. **Security:**
   - [ ] Change SECRET_KEY in .env
   - [ ] Update CORS origins (no wildcards)
   - [ ] Use HTTPS
   - [ ] Strong admin password

2. **Database:**
   - [ ] Run migrations on production DB
   - [ ] Set up backups
   - [ ] Configure connection pooling

3. **Monitoring:**
   - [ ] Set up error tracking (Sentry)
   - [ ] Configure logging
   - [ ] Monitor audit logs

4. **Performance:**
   - [ ] Enable caching
   - [ ] Set up rate limiting
   - [ ] Optimize database indexes

---

## Support Files

- `ADMIN_IMPLEMENTATION_COMPLETE.md` - Full documentation
- `verify_admin_setup.py` - Verification script
- `app/api/endpoints/admin.py` - All endpoint code
- `app/middleware/audit.py` - Audit logging code
- `app/schemas/admin.py` - Request/response schemas
- `app/api/deps.py` - Auth dependencies

---

**Ready to test? Run the commands in Step 1-5 above!**
