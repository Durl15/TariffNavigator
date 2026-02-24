# 🚀 TariffNavigator - Render Deployment Guide

**Deploy TariffNavigator to Render in 15 minutes!**

---

## ✅ Prerequisites

Before you start, make sure you have:
- [ ] GitHub account (your repo is already there!)
- [ ] Render account (sign up at https://render.com - it's free!)
- [ ] Required API keys (see below)

---

## 🔑 Required Environment Variables

You'll need these API keys and credentials:

### Essential (Required):
1. **OpenAI API Key** - For AI features
   - Get from: https://platform.openai.com/api-keys
   - Format: `sk-proj-...`

2. **SMTP Email Credentials** - For sending notifications
   - **Option 1: Mailtrap** (Recommended for testing)
     - Sign up: https://mailtrap.io
     - Get SMTP credentials from your inbox
   - **Option 2: SendGrid** (For production)
     - Sign up: https://sendgrid.com
     - Create API key and use as password

### Optional (For full features):
3. **Stripe Keys** - For payments (if you want billing)
   - Get from: https://dashboard.stripe.com/apikeys
   - Need: Secret Key, Publishable Key, Webhook Secret

---

## 📋 Step-by-Step Deployment

### Step 1: Prepare Your Repository

**Commit the updated render.yaml:**

```bash
cd /c/Projects/TariffNavigator
git add render.yaml
git commit -m "feat: Add production Render deployment configuration"
git push
```

### Step 2: Sign Up for Render

1. Go to https://render.com
2. Click **"Get Started"** or **"Sign Up"**
3. Choose **"Sign up with GitHub"**
4. Authorize Render to access your repositories

### Step 3: Create New Blueprint

1. From Render Dashboard, click **"New +"** → **"Blueprint"**
2. Connect your GitHub account if not already connected
3. Select your repository: **"TariffNavigator"**
4. Render will detect the `render.yaml` file automatically
5. Click **"Apply"**

### Step 4: Configure Environment Variables

Render will create 3 services:
- `tariffnavigator-backend` (Python API)
- `tariffnavigator-frontend` (React app)
- `tariffnavigator-db` (PostgreSQL database)

**For the Backend service**, add these environment variables:

#### In Render Dashboard:
1. Go to **"tariffnavigator-backend"** service
2. Click **"Environment"** tab
3. Add these variables (click **"Add Environment Variable"**):

```bash
# CORS and Frontend URL (REQUIRED)
CORS_ORIGINS=https://tariffnavigator-frontend.onrender.com
FRONTEND_URL=https://tariffnavigator-frontend.onrender.com

# OpenAI API (REQUIRED for AI features)
OPENAI_API_KEY=sk-proj-YOUR_KEY_HERE

# SMTP Email Settings (REQUIRED for notifications)
SMTP_HOST=sandbox.smtp.mailtrap.io
SMTP_PORT=2525
SMTP_USER=your_mailtrap_username
SMTP_PASSWORD=your_mailtrap_password
FROM_EMAIL=noreply@tariffnavigator.com
FROM_NAME=TariffNavigator

# Stripe (OPTIONAL - only if you want payments)
STRIPE_SECRET_KEY=sk_test_...
STRIPE_PUBLISHABLE_KEY=pk_test_...
STRIPE_WEBHOOK_SECRET=whsec_...
STRIPE_PRICE_ID_PRO=price_...
STRIPE_PRICE_ID_ENTERPRISE=price_...
```

**For the Frontend service**:
1. Go to **"tariffnavigator-frontend"** service
2. Click **"Environment"** tab
3. Update the `BACKEND_URL` variable:

```bash
BACKEND_URL=https://tariffnavigator-backend.onrender.com/api/v1
```

### Step 5: Deploy!

1. Click **"Manual Deploy"** → **"Deploy latest commit"** for both services
2. Wait for build to complete (5-10 minutes first time)
3. Check logs for any errors

### Step 6: Seed the Database

After the backend is deployed and running:

1. Go to **"tariffnavigator-backend"** service
2. Click **"Shell"** tab
3. Run these commands to add HS codes:

```bash
# Enter Python shell
python

# Then paste this code:
import asyncio
from app.db.seed_data import seed_if_empty
asyncio.run(seed_if_empty())
exit()
```

**Or** manually add HS codes via SQL:

Click **"tariffnavigator-db"** → **"Connect"** → Use the connection string to connect with a PostgreSQL client, then run:

```sql
-- Add China HS codes
INSERT INTO hs_codes (code, description, level, country, mfn_rate, general_rate, vat_rate, created_at) VALUES
('8703', 'Motor cars and other motor vehicles, passenger vehicles', 'tariff', 'CN', 0.15, 0.15, 0.13, NOW()),
('8517.12', 'Mobile phones including smartphones', 'tariff', 'CN', 0.00, 0.00, 0.13, NOW()),
('8471.30', 'Portable automatic data processing machines, laptops, tablets', 'tariff', 'CN', 0.00, 0.00, 0.13, NOW()),
('6402', 'Footwear with outer soles and uppers of rubber or plastics', 'tariff', 'CN', 0.13, 0.13, 0.13, NOW()),
('6109', 'T-shirts, singlets and other vests, knitted or crocheted', 'tariff', 'CN', 0.06, 0.06, 0.13, NOW())
ON CONFLICT (code, country) DO NOTHING;

-- Add EU HS codes
INSERT INTO hs_codes (code, description, level, country, mfn_rate, general_rate, vat_rate, created_at) VALUES
('8703', 'Motor cars and other motor vehicles, passenger vehicles', 'tariff', 'EU', 0.10, 0.10, 0.20, NOW()),
('8517.12', 'Mobile phones including smartphones', 'tariff', 'EU', 0.00, 0.00, 0.20, NOW()),
('8471.30', 'Portable automatic data processing machines, laptops, tablets', 'tariff', 'EU', 0.00, 0.00, 0.20, NOW()),
('6402', 'Footwear with outer soles and uppers of rubber or plastics', 'tariff', 'EU', 0.17, 0.17, 0.20, NOW()),
('6109', 'T-shirts, singlets and other vests, knitted or crocheted', 'tariff', 'EU', 0.12, 0.12, 0.20, NOW())
ON CONFLICT (code, country) DO NOTHING;
```

### Step 7: Test Your Deployment

1. **Get your URLs:**
   - Frontend: `https://tariffnavigator-frontend.onrender.com`
   - Backend: `https://tariffnavigator-backend.onrender.com`

2. **Test the frontend:**
   - Open the frontend URL in your browser
   - You should see the calculator page

3. **Test the API:**
   - Visit: `https://tariffnavigator-backend.onrender.com/api/v1/health`
   - Should return: `{"status":"healthy"}`

4. **Test a calculation:**
   - Search for "passenger"
   - Select a car code
   - Enter value "50000"
   - Click Calculate
   - Should see results!

---

## 🎉 Your App is Live!

**Share these URLs:**
- **Frontend**: https://tariffnavigator-frontend.onrender.com
- **API Docs**: https://tariffnavigator-backend.onrender.com/docs

---

## 🔧 Troubleshooting

### Issue: "Application failed to respond"
**Solution**: Check backend logs for errors. Make sure all environment variables are set.

### Issue: "CORS error" in browser console
**Solution**:
1. Go to backend service → Environment
2. Add/update: `CORS_ORIGINS=https://tariffnavigator-frontend.onrender.com`
3. Redeploy backend

### Issue: Calculator shows no results
**Solution**:
1. Check if HS codes are in database
2. Run the seed script from Step 6
3. Test API directly: `https://your-backend.onrender.com/api/v1/tariff/autocomplete?query=car&country=CN`

### Issue: "Database connection error"
**Solution**:
1. Make sure database service is running
2. Check that `DATABASE_URL` environment variable is connected to the database
3. Run migrations: Go to backend Shell → `alembic upgrade head`

### Issue: Free tier services sleeping
**Solution**:
- Render free tier services sleep after 15 minutes of inactivity
- First request takes ~30 seconds to wake up
- Consider upgrading to paid tier ($7/month) for always-on service
- Or use a service like UptimeRobot to ping your app every 10 minutes

---

## 💰 Cost Breakdown

### Free Tier (What you get):
- ✅ 750 hours/month web service time
- ✅ 100GB bandwidth
- ✅ PostgreSQL database (90 days free, then $7/month)
- ✅ Automatic HTTPS
- ✅ Custom domain support
- ⚠️ Services sleep after 15 minutes of inactivity

### Paid Tier ($7/month per service):
- ✅ Always-on (no sleeping)
- ✅ Faster deployments
- ✅ More resources (512MB RAM → 4GB RAM)

**Recommendation**: Start with free tier, upgrade if needed.

---

## 🔄 Updating Your App

When you push changes to GitHub:

```bash
git add .
git commit -m "feat: Add new feature"
git push
```

Render will **automatically** detect changes and redeploy! 🎉

**Manual deploy:**
1. Go to service in Render dashboard
2. Click "Manual Deploy" → "Deploy latest commit"

---

## 🌐 Custom Domain (Optional)

Want your own domain like `tariff.yourcompany.com`?

1. Buy a domain (Namecheap, Google Domains, etc.)
2. In Render Dashboard:
   - Go to your frontend service
   - Click "Settings" → "Custom Domains"
   - Add your domain
   - Update DNS records as instructed
3. Render provides free SSL certificates automatically!

---

## 📊 Monitoring

**View logs:**
1. Go to service in Render dashboard
2. Click "Logs" tab
3. See real-time logs

**Check health:**
- Backend: `https://your-backend.onrender.com/api/v1/health`
- Should return: `{"status":"healthy"}`

**Monitor usage:**
- Dashboard shows bandwidth, requests, and uptime

---

## ✅ Post-Deployment Checklist

- [ ] Both services deployed successfully
- [ ] Frontend loads in browser
- [ ] Backend health check returns 200
- [ ] Database has HS codes (run seed script)
- [ ] Calculator autocomplete works
- [ ] Can perform calculations
- [ ] Results display correctly
- [ ] All environment variables set
- [ ] CORS configured correctly
- [ ] Shared URLs with friends!

---

## 🆘 Need Help?

**Render Documentation**: https://render.com/docs
**Render Community**: https://community.render.com
**Status Page**: https://status.render.com

**Common issues solved**:
- Google: "render deployment failed python"
- Check Render docs for your specific error
- Look at deployment logs carefully

---

## 🎁 What to Share After Deployment

**Send this to your friends:**

```
Hey! Check out TariffNavigator - now live!

🌐 App: https://tariffnavigator-frontend.onrender.com
📖 User Guide: https://github.com/Durl15/TariffNavigator/blob/master/USER_GUIDE.md
⚡ Quick Reference: https://github.com/Durl15/TariffNavigator/blob/master/QUICK_REFERENCE.md

Try it:
1. Search "passenger"
2. Pick a car code
3. Enter "50000"
4. Calculate!

Free to use, no signup required! 🚀
```

---

**🎉 Congratulations! Your app is live!**

*Time to share with the world!* 🌍
