# Deployment Guide

## 🚀 One-Click Deploy

### Deploy Backend to Render
[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy?repo=https://github.com/Durl15/TariffNavigator)

### Deploy Frontend to Vercel
[![Deploy with Vercel](https://vercel.com/button)](https://vercel.com/new/clone?repository-url=https://github.com/Durl15/TariffNavigator&project-name=tariffnavigator&root-directory=frontend)

---

## 📋 Manual Deployment Steps

### Step 1: Deploy Backend (Render)

1. **Sign up at Render**: https://render.com
2. **Connect GitHub**: Authorize Render to access your repositories
3. **Create Web Service**:
   - Click "New +" → "Blueprint"
   - Select "TariffNavigator" repository
   - Render auto-detects `render.yaml`
   - Click "Apply"
4. **Wait for deployment** (~5-10 minutes)
5. **Note your backend URL**: `https://tariffnavigator-backend.onrender.com`

**Important**: After deployment, run database migrations:
- Go to Render dashboard → Your service → Shell
- Run: `alembic upgrade head`
- Run: `python scripts/create_admin_auto.py`

### Step 2: Deploy Frontend (Vercel)

1. **Sign up at Vercel**: https://vercel.com
2. **Import Project**:
   - Click "Add New..." → "Project"
   - Import from GitHub
   - Select "TariffNavigator"
3. **Configure Build Settings**:
   - Framework: Vite
   - Root Directory: `frontend`
   - Build Command: `npm run build`
   - Output Directory: `dist`
4. **Add Environment Variables**:
   - Click "Environment Variables"
   - Add: `VITE_API_URL` = `https://tariffnavigator-backend.onrender.com/api/v1`
5. **Deploy**: Click "Deploy"
6. **Your app is live!** ~2 minutes

### Step 3: Update CORS Settings

After deployment, update your backend CORS settings:

1. Go to Render dashboard → Your service → Environment
2. Add: `CORS_ORIGINS` = `https://your-app.vercel.app`
3. Redeploy backend

---

## 🔧 Alternative: Deploy to Railway

### Backend (Railway)

```bash
# Install Railway CLI
npm install -g @railway/cli

# Login
railway login

# Initialize
cd backend
railway init

# Deploy
railway up
```

### Get Database URL
```bash
railway variables
# Copy DATABASE_URL
```

---

## 🐳 Docker Deployment

Build and run with Docker:

```bash
# Backend
docker build -t tariffnavigator-backend ./backend
docker run -p 8000:8000 tariffnavigator-backend

# Frontend
docker build -t tariffnavigator-frontend ./frontend
docker run -p 3000:3000 tariffnavigator-frontend
```

---

## ✅ Post-Deployment Checklist

After deploying:

- [ ] Backend is accessible at your Render URL
- [ ] Frontend is accessible at your Vercel URL
- [ ] Database migrations ran successfully
- [ ] Admin user created (admin@test.com)
- [ ] CORS settings updated with frontend URL
- [ ] Environment variables set correctly
- [ ] Admin dashboard loads at `/admin`
- [ ] Can login with admin credentials
- [ ] Tariff calculator works

---

## 🌐 Your Live URLs

After deployment, you'll have:

- **Frontend**: `https://tariffnavigator-[random].vercel.app`
- **Backend API**: `https://tariffnavigator-backend.onrender.com`
- **Admin Dashboard**: `https://tariffnavigator-[random].vercel.app/admin`
- **API Docs**: `https://tariffnavigator-backend.onrender.com/docs`

---

## 🆘 Troubleshooting

### Backend Issues

**Database not initialized:**
```bash
# In Render Shell
alembic upgrade head
python scripts/create_admin_auto.py
```

**CORS errors:**
- Add your Vercel URL to `CORS_ORIGINS` environment variable

**Application crashes:**
- Check logs in Render dashboard
- Verify all environment variables are set

### Frontend Issues

**API calls failing:**
- Verify `VITE_API_URL` points to your Render backend
- Check CORS settings on backend

**Build fails:**
- Ensure Node.js version is 18+
- Check build logs for missing dependencies

**Blank page:**
- Check browser console for errors
- Verify routing configuration in `vercel.json`

---

## 💰 Cost Estimate

**Free Tier:**
- Render: Free (with some limitations)
- Vercel: Free (hobby tier)
- PostgreSQL: Free 100MB on Render

**Total: $0/month** for light usage

**Paid Tier (Optional):**
- Render Pro: $7/month (better performance)
- Vercel Pro: $20/month (team features)
- PostgreSQL: $7/month (1GB storage)

---

## 🔄 Updating Your Deployment

Push updates to GitHub:

```bash
git add .
git commit -m "Update feature"
git push origin master
```

Both Render and Vercel will auto-deploy from your `master` branch!

---

## 🎉 Success!

Share your live app:
- **App**: https://your-app.vercel.app
- **Admin**: https://your-app.vercel.app/admin
- **API**: https://your-backend.onrender.com/docs

Login: `admin@test.com` / `admin123`
