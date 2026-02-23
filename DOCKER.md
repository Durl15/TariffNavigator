# Docker Setup Guide

Complete guide for running TariffNavigator with Docker.

## Prerequisites

- **Docker Desktop** 4.0+ (Windows/Mac) or **Docker Engine** 20.10+ (Linux)
- **Docker Compose** v2.0+
- **4GB RAM** minimum (8GB recommended)
- **10GB free disk** space

### Install Docker

**Windows/Mac:**
1. Download [Docker Desktop](https://www.docker.com/products/docker-desktop)
2. Run installer and follow prompts
3. Verify: `docker --version` and `docker-compose --version`

**Linux (Ubuntu/Debian):**
```bash
# Install Docker
curl -fsSL https://get.docker.com | sudo sh
sudo usermod -aG docker $USER

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

---

## Quick Start (Development)

### 1. Clone and Configure

```bash
# Clone repository
git clone https://github.com/yourusername/TariffNavigator.git
cd TariffNavigator

# Copy environment template
cp .env.docker.example .env

# Edit .env and add your API keys
nano .env
```

**Required environment variables:**
- `OPENAI_API_KEY` - For AI features
- `STRIPE_SECRET_KEY` - Payment processing
- `STRIPE_PUBLISHABLE_KEY` - Frontend Stripe
- `SMTP_USER` - Email (Mailtrap for dev)
- `SMTP_PASSWORD` - Email password

### 2. Start All Services

```bash
docker-compose up --build
```

**What happens:**
1. Downloads base images (Python, Node, PostgreSQL, Nginx) - **2-3 min first time**
2. Builds backend image - **3-4 min**
3. Builds frontend image - **2-3 min**
4. Starts PostgreSQL database
5. Runs database migrations
6. Starts backend API (4 Gunicorn workers)
7. Starts frontend (Nginx)

**First run: 5-10 minutes. Subsequent runs: 30 seconds.**

### 3. Access Application

Once you see:
```
tariff_backend    | === Starting application server ===
tariff_frontend   | /docker-entrypoint.sh: Launching /docker-entrypoint.d/40-envsubst-on-templates.sh
```

**Services are ready:**
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **PostgreSQL**: localhost:5432

### 4. Test Credentials

```
Admin User:
Email: admin@test.com
Password: admin123

Regular User:
Email: test@test.com
Password: password123
```

### 5. Stop Services

```bash
# Stop containers (data persists)
docker-compose down

# Stop and remove volumes (deletes database)
docker-compose down -v
```

---

## Common Commands

### Service Management

```bash
# Start services (detached)
docker-compose up -d

# View real-time logs (all services)
docker-compose logs -f

# View logs for specific service
docker-compose logs -f backend
docker-compose logs -f frontend
docker-compose logs -f db

# Stop services
docker-compose down

# Restart single service
docker-compose restart backend

# Rebuild after code changes
docker-compose up --build

# View running containers
docker-compose ps

# View resource usage
docker stats
```

### Database Operations

```bash
# Access PostgreSQL shell
docker-compose exec db psql -U postgres -d tariff_nav

# Run migrations manually
docker-compose exec backend alembic upgrade head

# Create migration
docker-compose exec backend alembic revision --autogenerate -m "description"

# View migration history
docker-compose exec backend alembic history

# Database backup
docker-compose exec db pg_dump -U postgres tariff_nav > backup.sql

# Database restore
docker-compose exec -T db psql -U postgres tariff_nav < backup.sql
```

### Backend Shell Access

```bash
# Access backend container bash
docker-compose exec backend bash

# Run Python commands
docker-compose exec backend python -c "print('Hello')"

# Check installed packages
docker-compose exec backend pip list

# Run tests
docker-compose exec backend pytest
```

### Cleanup

```bash
# Remove stopped containers
docker-compose rm

# Remove all containers, volumes, images
docker-compose down -v --rmi all

# Clean Docker system (free disk space)
docker system prune -a --volumes
```

---

## Production Deployment

### Using docker-compose.prod.yml

**1. Create production .env file:**

```bash
cp .env.docker.example .env
nano .env
```

**Critical production settings:**
- `DATABASE_URL` - Managed PostgreSQL (AWS RDS, Azure Database)
- `SECRET_KEY` - 32+ random characters: `openssl rand -hex 32`
- `DEBUG=false`
- `CORS_ORIGINS` - Your actual domain(s)
- `VITE_API_URL` - Your backend API URL

**2. Build and run:**

```bash
# Build production images
docker-compose -f docker-compose.prod.yml build

# Start production stack
docker-compose -f docker-compose.prod.yml up -d

# Monitor logs
docker-compose -f docker-compose.prod.yml logs -f
```

**3. Health checks:**

```bash
# Backend health
curl http://localhost:8000/api/v1/health

# Frontend health
curl http://localhost:3000/health
```

### Using Individual Containers

**Build images:**

```bash
# Backend
docker build -t tariff-backend:latest ./backend

# Frontend
docker build -t tariff-frontend:latest \
  --build-arg VITE_API_URL=https://api.yourapp.com/api/v1 \
  ./frontend
```

**Run containers:**

```bash
# Backend (with external database)
docker run -d \
  -p 8000:8000 \
  -e DATABASE_URL="postgresql+asyncpg://user:pass@db.example.com:5432/tariff_nav" \
  -e SECRET_KEY="your-secret-key" \
  -e ENVIRONMENT="production" \
  -e DEBUG="false" \
  tariff-backend:latest

# Frontend
docker run -d \
  -p 3000:3000 \
  tariff-frontend:latest
```

---

## Troubleshooting

### Port Already in Use

**Error:** `bind: address already in use`

**Solution 1 - Kill process:**
```bash
# Find process using port
lsof -i :8000  # Mac/Linux
netstat -ano | findstr :8000  # Windows

# Kill process
kill -9 <PID>  # Mac/Linux
taskkill /PID <PID> /F  # Windows
```

**Solution 2 - Change port:**

Edit `docker-compose.yml`:
```yaml
ports:
  - "8001:8000"  # Map host port 8001 to container port 8000
```

### Database Connection Failed

**Error:** `could not connect to server: Connection refused`

**Check 1 - Database health:**
```bash
docker-compose logs db
docker-compose ps db
```

**Check 2 - Wait for database:**
```bash
# Database needs 10-20 seconds to initialize first time
docker-compose logs -f db | grep "ready to accept connections"
```

**Solution - Restart:**
```bash
docker-compose restart db
sleep 10
docker-compose restart backend
```

### Backend Won't Start

**Error:** Migrations fail or import errors

**Check logs:**
```bash
docker-compose logs backend
```

**Common issues:**

1. **Missing environment variables:**
   - Check .env file exists: `ls -la .env`
   - Verify required keys set: `cat .env | grep OPENAI_API_KEY`

2. **Database not ready:**
   - Wait 30 seconds after first `docker-compose up`
   - Check `docker-compose logs db`

3. **Migration errors:**
   ```bash
   # View migration status
   docker-compose exec backend alembic current

   # Try manual migration
   docker-compose exec backend alembic upgrade head
   ```

### Frontend Build Errors

**Error:** `npm ERR! code ELIFECYCLE`

**Solution 1 - Clear cache:**
```bash
docker-compose down
docker-compose build --no-cache frontend
docker-compose up
```

**Solution 2 - Check Node version:**
```bash
docker-compose exec frontend node --version  # Should be v18
```

### Container Keeps Restarting

**Check health status:**
```bash
docker-compose ps
# HEALTH column shows: starting, healthy, or unhealthy
```

**View restart reason:**
```bash
docker inspect --format='{{json .State}}' tariff_backend | jq
```

**Fix unhealthy containers:**
```bash
# Test health endpoint directly
docker-compose exec backend curl http://localhost:8000/api/v1/health

# If fails, check app logs
docker-compose logs backend --tail=100
```

### Out of Disk Space

**Check Docker disk usage:**
```bash
docker system df
```

**Clean up:**
```bash
# Remove unused containers, networks, images
docker system prune

# Remove everything (including volumes)
docker system prune -a --volumes

# Remove specific unused images
docker image prune -a
```

---

## Environment Variables

### Required for Development

| Variable | Example | Description |
|----------|---------|-------------|
| `OPENAI_API_KEY` | sk-... | OpenAI API for AI features |
| `STRIPE_SECRET_KEY` | sk_test_... | Stripe payment processing |
| `STRIPE_PUBLISHABLE_KEY` | pk_test_... | Frontend Stripe key |
| `SMTP_USER` | username | Email service username |
| `SMTP_PASSWORD` | password | Email service password |

### Required for Production

| Variable | Example | Description |
|----------|---------|-------------|
| `DATABASE_URL` | postgresql+asyncpg://... | Managed database connection |
| `SECRET_KEY` | 32+ random chars | JWT signing key |
| `CORS_ORIGINS` | https://yourapp.com | Allowed frontend origins |
| `FRONTEND_URL` | https://yourapp.com | Frontend URL for emails |
| `VITE_API_URL` | https://api.yourapp.com/api/v1 | Backend API URL |

### Optional

| Variable | Default | Description |
|----------|---------|-------------|
| `DEBUG` | true (dev), false (prod) | Debug mode |
| `ENVIRONMENT` | development | Environment name |
| `PORT` | 8000 | Backend port |
| `HOST` | 0.0.0.0 | Backend host |

---

## Performance Tuning

### Backend Workers

Adjust Gunicorn workers based on CPU cores:

**Formula:** `(2 * CPU_CORES) + 1`

Edit `backend/Dockerfile`:
```dockerfile
CMD ["gunicorn", "main:app", \
     "--workers", "8",  # Change this based on CPU cores
     "--worker-class", "uvicorn.workers.UvicornWorker", \
     ...
]
```

### Database Connection Pool

For high load, increase connection pool size.

Edit `backend/app/db/session.py`:
```python
engine = create_async_engine(
    DATABASE_URL,
    pool_size=20,  # Increase from default 5
    max_overflow=40,  # Increase from default 10
    pool_timeout=30,
    pool_recycle=3600
)
```

### Docker Resource Limits

Limit container resources to prevent one service from consuming all resources.

Add to `docker-compose.yml`:
```yaml
services:
  backend:
    deploy:
      resources:
        limits:
          cpus: '2.0'
          memory: 2G
        reservations:
          cpus: '0.5'
          memory: 512M
```

### Image Size Optimization

Current sizes:
- Backend: ~500MB (multi-stage build)
- Frontend: ~50MB (Alpine + Nginx)

**Further optimization:**
- Use `python:3.11-alpine` instead of `python:3.11-slim` (saves ~100MB)
- Compile Python dependencies on separate builder stage
- Remove dev dependencies from final image

---

## Security Checklist

### Production Deployment

- [ ] Change `SECRET_KEY` to random 32+ character string
- [ ] Set `DEBUG=false` in production
- [ ] Use managed PostgreSQL (not Docker container)
- [ ] Configure `CORS_ORIGINS` to only your domain (no wildcards)
- [ ] Use HTTPS (add reverse proxy like Traefik/Nginx)
- [ ] Rotate API keys regularly
- [ ] Enable Docker secrets for sensitive data
- [ ] Set up log aggregation (ELK, CloudWatch, Datadog)
- [ ] Configure firewall rules (only expose 80/443)
- [ ] Enable automatic security updates
- [ ] Scan images for vulnerabilities: `docker scan tariff-backend`
- [ ] Use non-root user in containers
- [ ] Implement rate limiting (handled by backend)
- [ ] Set up database backups (automated daily)
- [ ] Enable monitoring and alerting

### Docker-specific Security

```bash
# Scan for vulnerabilities
docker scan tariff-backend:latest
docker scan tariff-frontend:latest

# Use Docker secrets
echo "my-secret-key" | docker secret create secret_key -
docker service create --secret secret_key myservice

# Run containers as non-root
# Already configured in Dockerfiles with USER directive
```

---

## Advanced Topics

### Hot Reload Development

The development docker-compose.yml mounts source code as volumes for hot reload:

```yaml
volumes:
  - ./backend:/app  # Backend code changes reload automatically
```

**Backend** - Gunicorn auto-reloads on file changes
**Frontend** - Nginx serves static build (rebuild required)

To rebuild frontend after changes:
```bash
docker-compose up --build frontend
```

### Multi-stage Builds

Our Dockerfiles use multi-stage builds to reduce image size:

**Stage 1 (builder):** Installs dependencies, builds app
**Stage 2 (runtime):** Copies only compiled artifacts

**Benefits:**
- 80% smaller images (no build tools in final image)
- Faster deployments
- More secure (less attack surface)

### Custom Networks

Create custom Docker network for service isolation:

```bash
# Create network
docker network create tariff-network

# Use in docker-compose.yml
services:
  backend:
    networks:
      - tariff-network

networks:
  tariff-network:
    external: true
```

### Kubernetes Migration

To deploy to Kubernetes:

1. Push images to registry:
```bash
docker tag tariff-backend:latest your-registry/tariff-backend:latest
docker push your-registry/tariff-backend:latest
```

2. Convert compose to K8s manifests:
```bash
kompose convert -f docker-compose.yml
```

3. Deploy to cluster:
```bash
kubectl apply -f backend-deployment.yaml
kubectl apply -f frontend-deployment.yaml
kubectl apply -f backend-service.yaml
kubectl apply -f frontend-service.yaml
```

---

## FAQ

### Q: How do I update the application?

```bash
git pull
docker-compose down
docker-compose up --build
```

### Q: Can I use SQLite instead of PostgreSQL?

Development only (not recommended):
```yaml
environment:
  DATABASE_URL: sqlite+aiosqlite:///./tariffnavigator.db
```

Remove `depends_on: db` and comment out db service.

### Q: How do I access the database from my host machine?

```bash
# PostgreSQL
psql -h localhost -p 5432 -U postgres -d tariff_nav
# Password: postgres

# Or use GUI tools (DBeaver, pgAdmin)
# Host: localhost
# Port: 5432
# User: postgres
# Password: postgres
# Database: tariff_nav
```

### Q: Can I run only backend or frontend?

```bash
# Only backend (with database)
docker-compose up db backend

# Only frontend
docker-compose up frontend
```

### Q: How do I debug inside a container?

```bash
# Python debugger (pdb)
docker-compose exec backend python -m pdb /app/main.py

# Interactive Python shell
docker-compose exec backend python

# Install additional tools
docker-compose exec backend pip install ipython
docker-compose exec backend ipython
```

### Q: How do I test the production build locally?

```bash
# Create production .env
cp .env.docker.example .env
# Edit with production-like values

# Run production compose
docker-compose -f docker-compose.prod.yml up

# Test
curl http://localhost:8000/api/v1/health
```

---

## Next Steps

After Docker setup is working:

1. **CI/CD Pipeline** - Automate builds and deployments (GitHub Actions)
2. **Kubernetes** - Deploy to Kubernetes for production scaling
3. **Monitoring** - Add Prometheus + Grafana for metrics
4. **Logging** - Implement ELK stack for log aggregation
5. **Backups** - Automate database backups
6. **CDN** - Add CloudFront/Cloudflare for static assets
7. **Load Balancer** - Add for high availability

---

## Support

For issues or questions:
- GitHub Issues: https://github.com/yourusername/TariffNavigator/issues
- Documentation: https://github.com/yourusername/TariffNavigator
- Docker Docs: https://docs.docker.com
