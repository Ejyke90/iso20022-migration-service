# Deployment Guide: Vercel + Railway

Deploy your Word to PDF web application to the cloud for free! Users will access it via a URL with no installation required.

## 🏗️ Architecture

```
┌─────────────────────────────────────────────┐
│  Users access: wordtopdf.vercel.app         │
└─────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────┐
│  Frontend (Next.js) - Hosted on Vercel      │
│  - Beautiful UI                             │
│  - File upload interface                    │
│  - Download handling                        │
└─────────────────────────────────────────────┘
                    ↓ API calls
┌─────────────────────────────────────────────┐
│  Backend (Flask) - Hosted on Railway        │
│  - File conversion                          │
│  - PDF generation                           │
│  - File cleanup                             │
└─────────────────────────────────────────────┘
```

---

## Part 1: Deploy Backend to Railway

### Step 1: Prepare Backend for Deployment

First, create a `railway.json` configuration file:

```bash
cd /path/to/word-to-pdf-agent
```

Create `api/railway.json`:
```json
{
  "$schema": "https://railway.app/railway.schema.json",
  "build": {
    "builder": "NIXPACKS"
  },
  "deploy": {
    "startCommand": "gunicorn -w 4 -b 0.0.0.0:$PORT api.server:app",
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 10
  }
}
```

### Step 2: Update requirements.txt

Add Gunicorn (production server) to `api/requirements.txt`:
```
Flask==3.0.0
Flask-CORS==4.0.0
Werkzeug==3.0.1
gunicorn==21.2.0
docx2pdf==0.1.8
```

### Step 3: Create Procfile (Alternative)

Create `api/Procfile`:
```
web: gunicorn -w 4 -b 0.0.0.0:$PORT api.server:app
```

### Step 4: Deploy to Railway

1. **Sign up for Railway**
   - Go to https://railway.app
   - Sign up with GitHub (free account)

2. **Create New Project**
   - Click "New Project"
   - Select "Deploy from GitHub repo"
   - Connect your GitHub account
   - Select your `word-to-pdf-agent` repository

3. **Configure Service**
   - Railway will auto-detect Python
   - Set **Root Directory**: `api`
   - Set **Start Command**: `gunicorn -w 4 -b 0.0.0.0:$PORT server:app`

4. **Add Environment Variables**
   - Click "Variables" tab
   - Add:
     ```
     PYTHONUNBUFFERED=1
     PORT=5000
     ```

5. **Deploy**
   - Click "Deploy"
   - Wait for build to complete (2-3 minutes)
   - Copy your Railway URL (e.g., `https://word-to-pdf-api.railway.app`)

### Step 5: Test Backend

Test your deployed API:
```bash
curl https://your-railway-url.railway.app/api/health
```

Should return:
```json
{"status": "healthy", "message": "Word to PDF API is running"}
```

---

## Part 2: Deploy Frontend to Vercel

### Step 1: Update Frontend API URL

Update `web-app/app/page.tsx` to use your Railway backend URL:

Find this line (around line 45):
```typescript
const response = await fetch('http://localhost:5000/api/convert', {
```

Replace with:
```typescript
const response = await fetch('https://YOUR-RAILWAY-URL.railway.app/api/convert', {
```

And update the download URL (around line 54):
```typescript
setDownloadUrl(`https://YOUR-RAILWAY-URL.railway.app${data.download_url}`);
```

### Step 2: Create Environment Variable (Better Approach)

Create `web-app/.env.local`:
```env
NEXT_PUBLIC_API_URL=https://your-railway-url.railway.app
```

Update `web-app/app/page.tsx` to use environment variable:
```typescript
const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:5000';

// Then use it:
const response = await fetch(`${API_URL}/api/convert`, {
  method: 'POST',
  body: formData,
});

setDownloadUrl(`${API_URL}${data.download_url}`);
```

### Step 3: Deploy to Vercel

1. **Sign up for Vercel**
   - Go to https://vercel.com
   - Sign up with GitHub (free account)

2. **Import Project**
   - Click "Add New..." → "Project"
   - Import your `word-to-pdf-agent` repository
   - Vercel will auto-detect Next.js

3. **Configure Build Settings**
   - **Framework Preset**: Next.js
   - **Root Directory**: `web-app`
   - **Build Command**: `npm run build`
   - **Output Directory**: `.next`

4. **Add Environment Variables**
   - Click "Environment Variables"
   - Add:
     ```
     NEXT_PUBLIC_API_URL=https://your-railway-url.railway.app
     ```

5. **Deploy**
   - Click "Deploy"
   - Wait for build (2-3 minutes)
   - Your site will be live at `https://your-project.vercel.app`

### Step 4: Update CORS on Backend

Update Railway backend to allow your Vercel domain.

In `api/server.py`, update CORS configuration:
```python
from flask_cors import CORS

app = Flask(__name__)
CORS(app, origins=[
    "http://localhost:3000",
    "https://your-project.vercel.app",
    "https://*.vercel.app"  # Allow all Vercel preview deployments
])
```

Redeploy to Railway (push to GitHub or use Railway CLI).

---

## Part 3: Custom Domain (Optional)

### For Vercel (Frontend)

1. Go to your Vercel project
2. Click "Settings" → "Domains"
3. Add your custom domain (e.g., `wordtopdf.com`)
4. Follow DNS configuration instructions
5. Update `NEXT_PUBLIC_API_URL` if needed

### For Railway (Backend)

1. Go to your Railway project
2. Click "Settings" → "Domains"
3. Add custom domain (e.g., `api.wordtopdf.com`)
4. Update DNS records as instructed
5. Update frontend environment variable

---

## Part 4: Continuous Deployment

Both Vercel and Railway support automatic deployments:

### Automatic Deployment Flow

1. **Push to GitHub**
   ```bash
   git add .
   git commit -m "Update feature"
   git push origin main
   ```

2. **Automatic Build**
   - Vercel rebuilds frontend automatically
   - Railway rebuilds backend automatically

3. **Live in Minutes**
   - Changes are live within 2-3 minutes
   - Zero downtime deployments

---

## 🎯 Final Checklist

- [ ] Backend deployed to Railway
- [ ] Backend API health check works
- [ ] Frontend deployed to Vercel
- [ ] Environment variables configured
- [ ] CORS updated with Vercel URL
- [ ] Test file upload and conversion
- [ ] Test PDF download
- [ ] (Optional) Custom domain configured

---

## 💰 Pricing

### Free Tier Limits

**Vercel (Frontend)**
- ✅ Unlimited deployments
- ✅ 100 GB bandwidth/month
- ✅ Automatic HTTPS
- ✅ Custom domains

**Railway (Backend)**
- ✅ $5 free credits/month
- ✅ ~500 hours of usage
- ✅ Automatic HTTPS
- ✅ Custom domains

**Total Cost**: **FREE** for moderate usage!

---

## 🚀 Your Live URLs

After deployment, you'll have:

- **Frontend**: `https://your-project.vercel.app`
- **Backend API**: `https://your-api.railway.app`
- **Documentation**: `https://ejyke90.github.io/word-to-pdf-agent/`

Share the Vercel URL with users - they can start converting documents immediately!

---

## 📞 Support

If you encounter issues:

1. **Vercel Logs**: Check build logs in Vercel dashboard
2. **Railway Logs**: Check runtime logs in Railway dashboard
3. **CORS Issues**: Verify backend CORS configuration
4. **Environment Variables**: Double-check all URLs

---

## 🔄 Updating Your App

To push updates:

```bash
# Make changes to your code
git add .
git commit -m "Your update message"
git push origin main

# Both Vercel and Railway will auto-deploy!
```

---

**Congratulations! Your Word to PDF converter is now live and accessible to anyone with internet access!** 🎉
