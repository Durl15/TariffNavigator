# Quick Setup Guide for Friends

## One-Time Setup (5 minutes)

### Step 1: Clone the Repository
```bash
git clone https://github.com/Durl15/TariffNavigator.git
cd TariffNavigator
```

### Step 2: Setup Backend
```bash
cd backend

# Create virtual environment
python -m venv .venv

# Activate it
# Windows:
.venv\Scripts\activate
# Mac/Linux:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Setup database
alembic upgrade head

# Create admin user
python scripts/create_admin_auto.py

# Start backend
uvicorn main:app --reload
```

Backend running at: http://localhost:8000

### Step 3: Setup Frontend (in new terminal)
```bash
cd frontend

# Install dependencies
npm install

# Start frontend
npm run dev
```

Frontend running at: http://localhost:3001

### Step 4: Login
- Go to: http://localhost:3001/admin
- Email: `admin@test.com`
- Password: `admin123`

## That's it! 🎉

You now have:
- ✅ Tariff calculator at http://localhost:3001
- ✅ Admin dashboard at http://localhost:3001/admin
- ✅ API docs at http://localhost:8000/docs

## Troubleshooting

**Backend won't start?**
- Make sure Python 3.10+ is installed: `python --version`
- Check if port 8000 is free

**Frontend won't start?**
- Make sure Node.js 18+ is installed: `node --version`
- Try deleting `node_modules` and running `npm install` again

**Database errors?**
- Delete `backend/tariff_navigator.db` and run `alembic upgrade head` again

## Need Help?
Open an issue on GitHub: https://github.com/Durl15/TariffNavigator/issues
