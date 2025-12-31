# Railway Deployment - Step by Step Guide

## 🚂 Deploy Your Backend to Railway

### Step 1: Push Your Code to GitHub

First, make sure all your changes are committed and pushed:

```bash
cd /Users/ejikeudeze/.gemini/antigravity/scratch/word-to-pdf-agent

# Add all files
git add .

# Commit
git commit -m "Prepare for Railway deployment"

# Push to GitHub
git push origin main
```

---

### Step 2: Create New Project on Railway

1. Go to **https://railway.app/dashboard**
2. Click **"New Project"**
3. Select **"Deploy from GitHub repo"**
4. If prompted, click **"Configure GitHub App"** and authorize Railway
5. Select your repository: **`word-to-pdf-agent`**

---

### Step 3: Configure the Service

Railway will start deploying automatically, but we need to configure it:

#### 3a. Set Root Directory (IMPORTANT!)

1. Click on your service (should show "word-to-pdf-agent")
2. Go to **Settings** tab
3. Scroll to **"Root Directory"**
4. Leave it **BLANK** (empty) - this is important!
5. Click **"Update"**

#### 3b. Verify Start Command

1. Still in **Settings** tab
2. Scroll to **"Start Command"**
3. It should auto-detect or you can set it to:
   ```
   gunicorn -w 4 -b 0.0.0.0:$PORT api.server:app
   ```
4. Click **"Update"** if you changed it

#### 3c. Add Environment Variables

1. Click **"Variables"** tab
2. Click **"+ New Variable"**
3. Add these variables:

   **Variable 1:**
   - Name: `PYTHONUNBUFFERED`
   - Value: `1`

   **Variable 2:**
   - Name: `PORT`
   - Value: `5000`

4. Click **"Add"** for each

---

### Step 4: Deploy

1. Go to **"Deployments"** tab
2. Railway should automatically start building
3. Wait 2-3 minutes for the build to complete
4. Look for **"Success"** status

---

### Step 5: Get Your Railway URL

1. Go to **"Settings"** tab
2. Scroll to **"Domains"** section
3. Click **"Generate Domain"**
4. Copy your Railway URL (e.g., `https://word-to-pdf-agent-production.up.railway.app`)

---

### Step 6: Test Your API

Open a new browser tab and test:

```
https://YOUR-RAILWAY-URL.railway.app/api/health
```

You should see:
```json
{
  "status": "healthy",
  "message": "Word to PDF API is running"
}
```

✅ **If you see this, your backend is live!**

---

### Step 7: Save Your Railway URL

Copy your Railway URL - you'll need it for Vercel deployment:

```
https://YOUR-APP-NAME.up.railway.app
```

---

## 🐛 Troubleshooting

### If Build Fails:

1. **Check Logs**: Click "Deployments" → Click on the failed deployment → View logs
2. **Common Issues**:
   - Missing dependencies: Check `api/requirements.txt`
   - Wrong start command: Verify it's `gunicorn -w 4 -b 0.0.0.0:$PORT api.server:app`
   - Root directory: Should be empty (project root)

### If "main.py" Error Appears:

This means Railway is running the wrong file. Fix:
1. Go to **Settings** → **Start Command**
2. Set to: `gunicorn -w 4 -b 0.0.0.0:$PORT api.server:app`
3. Redeploy

### If CORS Errors:

The backend is already configured for CORS. If you still see errors:
1. Check that your frontend URL is in the CORS list in `api/server.py`
2. Redeploy after making changes

---

## ✅ Success Checklist

- [ ] Code pushed to GitHub
- [ ] Railway project created
- [ ] Root directory set (empty)
- [ ] Start command configured
- [ ] Environment variables added
- [ ] Deployment successful
- [ ] Health check returns success
- [ ] Railway URL copied

---

## 🎯 Next Steps

Once your Railway backend is deployed:

1. **Copy your Railway URL**
2. **Deploy frontend to Vercel** (see DEPLOYMENT_GUIDE.md Part 2)
3. **Add Railway URL to Vercel** as `NEXT_PUBLIC_API_URL`

Your app will be live! 🚀
