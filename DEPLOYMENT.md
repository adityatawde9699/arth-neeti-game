# Deployment Guide

## Quick Deploy

### Backend → Render.com (Free)
### Frontend → Vercel (Free)

---

## 🚀 Backend Deployment (Render)

### Step 1: Create PostgreSQL Database

1. Go to [Render Dashboard](https://dashboard.render.com)
2. Click **New → PostgreSQL**
3. Settings:
   - Name: `arth-neeti-db`
   - Region: Singapore (closest to India)
   - Plan: Free
4. Click **Create Database**
5. Copy the **Internal Database URL**

### Step 2: Deploy Backend

1. Click **New → Web Service**
2. Connect your GitHub repo
3. Settings:
   - **Name**: `arth-neeti-api`
   - **Region**: Singapore
   - **Branch**: main
   - **Root Directory**: `arth-neeti-game/backend`
   - **Runtime**: Python 3
   - **Build Command**: `./build.sh`
   - **Start Command**: `gunicorn core.wsgi:application`
4. **Environment Variables**:
   ```
   SECRET_KEY=<generate-a-random-key>
   DEBUG=False
   DATABASE_URL=<paste-internal-database-url>
   CORS_ALLOWED_ORIGINS=https://your-frontend.vercel.app
   ```
5. Click **Create Web Service**

### Generate Secret Key
```python
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

---

## 🌐 Frontend Deployment (Vercel)

### Step 1: Deploy to Vercel

1. Go to [vercel.com](https://vercel.com)
2. Click **Add New → Project**
3. Import your GitHub repo
4. Settings:
   - **Framework Preset**: Vite
   - **Root Directory**: `arth-neeti-game/frontend`
5. **Environment Variables**:
   ```
   VITE_API_URL=https://arth-neeti-api.onrender.com/api
   ```
6. Click **Deploy**

---

## 🔧 Post-Deployment Checklist

- [ ] Backend is live at `https://arth-neeti-api.onrender.com`
- [ ] Frontend is live at `https://arth-neeti.vercel.app`
- [ ] Game starts successfully
- [ ] All API calls work
- [ ] Update CORS_ALLOWED_ORIGINS with actual Vercel URL

---

## 📊 Environment Variables Summary

### Backend (Render)
| Variable | Value |
|----------|-------|
| `SECRET_KEY` | Random 50-char string |
| `DEBUG` | `False` |
| `DATABASE_URL` | PostgreSQL internal URL |
| `CORS_ALLOWED_ORIGINS` | Your Vercel frontend URL |

### Frontend (Vercel)
| Variable | Value |
|----------|-------|
| `VITE_API_URL` | Your Render backend URL + `/api` |

---

## 🔄 Updating Deployments

Both services auto-deploy when you push to `main`:

```bash
git add .
git commit -m "Update feature"
git push origin main
```

---

## 💡 Tips

1. **Cold Starts**: Render free tier sleeps after 15 min inactivity. First request takes ~30s.
2. **Database**: Free PostgreSQL expires after 90 days. Backup data!
3. **Custom Domain**: Both Render & Vercel support custom domains (free).
