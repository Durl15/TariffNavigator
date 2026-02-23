# TariffNavigator

AI-powered tariff calculator with comprehensive admin dashboard for user and organization management.

## Overview

TariffNavigator is a full-stack web application that helps businesses calculate import tariffs, duties, and taxes for international trade. It features multi-currency support, FTA (Free Trade Agreement) checks, HS code autocomplete, and a powerful admin panel for managing users and organizations.

## Features

### Tariff Calculator
- 🌍 **Multi-Country Support**: China (CN) and European Union (EU)
- 💱 **Multi-Currency**: USD, CNY, EUR, JPY, GBP, KRW with live exchange rates
- 🔍 **HS Code Autocomplete**: Smart search for harmonized system codes
- 📊 **Detailed Breakdowns**: CIF value, customs duty, VAT, consumption tax
- 🤝 **FTA Checker**: Automatic detection of Free Trade Agreement benefits
- 📈 **Real-time Calculations**: Instant tariff and duty calculations

### Admin Dashboard
- 👥 **User Management**: Full CRUD operations with search and filtering
- 🏢 **Organization Management**: Track usage, quotas, and billing plans
- 📊 **Real-time Statistics**: System metrics, activity tracking, and analytics
- 📝 **Audit Logging**: Comprehensive activity logs with filtering
- 🔐 **Role-Based Access**: Viewer, User, Admin, and Super Admin roles
- 🔍 **Advanced Search**: Filter users by role, status, and organization
- 📱 **Responsive Design**: Works seamlessly on desktop and mobile

## Tech Stack

### Frontend
- **React 18** - Modern UI library
- **TypeScript** - Type-safe development
- **Vite** - Fast build tool and dev server
- **React Router v6** - Client-side routing
- **TanStack Query** - Efficient data fetching and caching
- **Axios** - HTTP client with interceptors
- **Tailwind CSS** - Utility-first styling
- **Lucide React** - Beautiful icons
- **React Hot Toast** - Toast notifications

### Backend
- **FastAPI** - High-performance Python web framework
- **SQLAlchemy 2.0** - Async ORM
- **Pydantic v2** - Data validation
- **PostgreSQL/SQLite** - Database
- **Alembic** - Database migrations
- **JWT** - Authentication with python-jose
- **Bcrypt** - Password hashing
- **CORS** - Cross-origin resource sharing

## 🐳 Quick Start with Docker (Recommended)

The fastest way to run TariffNavigator is with Docker. No need to install Python, Node.js, or PostgreSQL manually.

### Prerequisites
- Docker Desktop 4.0+ (Windows/Mac) or Docker Engine 20.10+ (Linux)
- Docker Compose v2.0+
- 4GB RAM minimum

### Setup Steps

```bash
# 1. Clone repository
git clone https://github.com/yourusername/TariffNavigator.git
cd TariffNavigator

# 2. Configure environment
cp .env.docker.example .env
# Edit .env and add your API keys (OPENAI_API_KEY, STRIPE keys, SMTP credentials)

# 3. Start all services
docker-compose up
```

**First run takes 5-10 minutes** (downloading images, building). Subsequent runs take ~30 seconds.

### Access the Application

Once started:
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

### Default Credentials

```
Admin:
Email: admin@test.com
Password: admin123

User:
Email: test@test.com
Password: password123
```

### Common Commands

```bash
# Stop services
docker-compose down

# View logs
docker-compose logs -f

# Restart services
docker-compose restart

# Rebuild after code changes
docker-compose up --build
```

**For detailed Docker documentation**, see [DOCKER.md](./DOCKER.md)

---

## Installation (Manual Setup)

If you prefer not to use Docker, follow these manual installation steps:

### Prerequisites
- Python 3.10+
- Node.js 18+
- npm or yarn
- PostgreSQL 15+ (or SQLite for development)

### Backend Setup

```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv .venv

# Activate virtual environment
# Windows:
.venv\Scripts\activate
# Linux/Mac:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run database migrations
alembic upgrade head

# Create admin user
python scripts/create_admin_auto.py

# Start the server
uvicorn main:app --reload
```

Backend will be available at: `http://localhost:8000`

### Frontend Setup

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

Frontend will be available at: `http://localhost:3001`

## Usage

### Accessing the Application

- **Main Calculator**: http://localhost:3001
- **Admin Dashboard**: http://localhost:3001/admin
- **API Documentation**: http://localhost:8000/docs
- **API Redoc**: http://localhost:8000/redoc

### Default Admin Credentials

```
Email: admin@test.com
Password: admin123
```

⚠️ **Important**: Change these credentials in production!

### Using the Tariff Calculator

1. Select destination country (China or EU)
2. Choose currency for calculations
3. Search for product or HS code using autocomplete
4. Enter CIF value in USD
5. Click "Calculate" to get detailed breakdown
6. Optionally check FTA benefits for origin country

### Using the Admin Dashboard

1. Log in with admin credentials
2. Navigate through the sidebar:
   - **Dashboard**: View system statistics
   - **Users**: Manage user accounts
   - **Organizations**: Track organization usage
   - **Audit Logs**: Review system activity

## API Endpoints

### Authentication
- `POST /api/v1/auth/login` - User login
- `POST /api/v1/auth/register` - User registration

### Tariff Calculator
- `GET /api/v1/tariff/autocomplete` - HS code search
- `POST /api/v1/tariff/calculate-with-currency` - Calculate tariffs
- `GET /api/v1/tariff/fta-check` - Check FTA eligibility

### Admin Panel (Requires Authentication)
- `GET /api/v1/admin/stats` - System statistics
- `GET /api/v1/admin/users` - List users (paginated)
- `POST /api/v1/admin/users` - Create user
- `PUT /api/v1/admin/users/{id}` - Update user
- `DELETE /api/v1/admin/users/{id}` - Delete user
- `GET /api/v1/admin/organizations` - List organizations
- `POST /api/v1/admin/organizations` - Create organization
- `GET /api/v1/admin/audit-logs` - View audit logs

Full API documentation available at `/docs` when running the backend.

## Database Schema

### Key Models

- **User**: User accounts with roles and authentication
- **Organization**: Companies with usage quotas and plans
- **Calculation**: Stored tariff calculations
- **AuditLog**: System activity tracking
- **HSCode**: Harmonized system code database

## Configuration

### Backend Configuration

Edit `backend/.env`:

```env
DATABASE_URL=sqlite:///./tariff_navigator.db
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=10080
```

### Frontend Configuration

Edit `frontend/.env`:

```env
VITE_API_URL=http://localhost:8000/api/v1
```

## Development

### Running Tests

```bash
# Backend tests
cd backend
pytest

# Frontend tests
cd frontend
npm test
```

### Database Migrations

```bash
# Create new migration
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head

# Rollback migration
alembic downgrade -1
```

### Code Quality

```bash
# Backend linting
cd backend
black .
flake8 .

# Frontend linting
cd frontend
npm run lint
```

## Deployment

### Production Checklist

- [ ] Change default admin credentials
- [ ] Set strong SECRET_KEY in environment variables
- [ ] Use PostgreSQL instead of SQLite
- [ ] Enable HTTPS/SSL
- [ ] Configure CORS properly
- [ ] Set up backup strategy for database
- [ ] Configure logging and monitoring
- [ ] Set up rate limiting
- [ ] Review security headers
- [ ] Enable database connection pooling

### Docker Deployment (Optional)

```bash
# Build and run with Docker Compose
docker-compose up -d
```

## Security Features

- 🔐 JWT-based authentication
- 🔑 Bcrypt password hashing
- 🛡️ Role-based access control (RBAC)
- 📝 Comprehensive audit logging
- 🚫 SQL injection protection via ORM
- ✅ Input validation with Pydantic
- 🔒 CORS configuration
- 🕐 Token expiration

## Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## Roadmap

- [ ] Add more countries and HS code databases
- [ ] Implement bulk calculation uploads
- [ ] Add export functionality for reports
- [ ] Create mobile app version
- [ ] Add real-time exchange rate API integration
- [ ] Implement advanced analytics dashboard
- [ ] Add email notifications for users
- [ ] Create API rate limiting
- [ ] Add two-factor authentication (2FA)
- [ ] Implement calculation history tracking

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For issues, questions, or contributions, please:
- Open an issue on GitHub
- Contact: [Your Email]
- Documentation: [Link to docs]

## Acknowledgments

- Built with FastAPI and React
- HS code data sourced from customs databases
- Icons by Lucide React
- UI components styled with Tailwind CSS

---

**Made with ❤️ by the TariffNavigator Team**
