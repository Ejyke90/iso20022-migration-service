# Fixing CORS and 502 Errors

## Issues Identified

1. **CORS Error**: Backend wasn't properly configured to allow all routes (only `/api/*` was allowed)
2. **502 Bad Gateway**: Backend server may not be running or properly deployed on Railway

## Fixes Applied

### 1. Backend (API) Changes

#### Updated CORS Configuration
- Changed from `r"/api/*"` to `r"/*"` to allow all routes
- Added `Content-Disposition` to exposed headers for file downloads
- Removed duplicate Vercel origins
- Added better CORS preflight handling with OPTIONS endpoint

#### Added Better Error Handling
- Enhanced logging throughout the API
- Added OPTIONS handler for `/api/convert` endpoint
- Better error messages with stack traces in logs
- Version info in health check endpoint

### 2. Frontend (Web App) Changes

#### Created `.env.local` File
- Set `NEXT_PUBLIC_API_URL` to your Railway backend URL
- This ensures the frontend always points to the correct backend

## Deployment Steps

### For Railway (Backend)

1. **Verify the backend is running**:
   ```bash
   curl https://doc-to-pdf-convertor-production.up.railway.app/api/health
   ```
   
   Expected response:
   ```json
   {
     "status": "healthy",
     "message": "Word to PDF API is running",
     "version": "1.0.0"
   }
   ```

2. **If backend is not running, redeploy**:
   - Go to your Railway dashboard
   - Navigate to your service
   - Click "Deploy" to trigger a new deployment
   - Check logs for any errors

3. **Common Railway Issues**:
   - Ensure `requirements.txt` is in the `api/` folder
   - Verify `Procfile` exists: `web: gunicorn server:app`
   - Check that Python version is specified in `runtime.txt`
   - Make sure the service has enough resources (not sleeping)

### For Vercel (Frontend)

1. **Add Environment Variable in Vercel**:
   - Go to Vercel Dashboard → Your Project → Settings → Environment Variables
   - Add: `NEXT_PUBLIC_API_URL` = `https://doc-to-pdf-convertor-production.up.railway.app`
   - Apply to: Production, Preview, and Development

2. **Redeploy the frontend**:
   ```bash
   cd web-app
   vercel --prod
   ```

### For Local Development

1. **Start the backend**:
   ```bash
   cd api
   python server.py
   ```

2. **In another terminal, start the frontend**:
   ```bash
   cd web-app
   npm run dev
   ```

3. **For local testing, update `.env.local`**:
   ```
   NEXT_PUBLIC_API_URL=http://localhost:5000
   ```

## Testing the Fix

### 1. Test Backend Directly

```bash
# Health check
curl https://doc-to-pdf-convertor-production.up.railway.app/api/health

# Test CORS preflight
curl -X OPTIONS https://doc-to-pdf-convertor-production.up.railway.app/api/convert \
  -H "Origin: https://word-to-pdf-agent.vercel.app" \
  -H "Access-Control-Request-Method: POST" \
  -v
```

### 2. Test Full Conversion Flow

1. Visit: https://word-to-pdf-agent.vercel.app
2. Upload a .docx file
3. Click "Convert to PDF"
4. Download should work without CORS or 502 errors

## Troubleshooting

### Still Getting CORS Errors?

1. **Clear browser cache** (hard refresh: Cmd+Shift+R on Mac, Ctrl+Shift+R on Windows)
2. **Check browser console** for the exact error
3. **Verify environment variable** in Vercel dashboard
4. **Ensure backend is deployed** with the new CORS configuration

### Still Getting 502 Errors?

1. **Check Railway logs**:
   - Railway Dashboard → Service → Deployments → View Logs
   - Look for Python errors or import failures

2. **Common causes**:
   - Backend crashed on startup
   - Missing dependencies in `requirements.txt`
   - Port binding issues (Railway automatically assigns PORT)
   - Memory/resource limits exceeded

3. **Fix for Railway deployment**:
   - Ensure `gunicorn` is properly configured
   - Check that `server:app` points to the Flask app
   - Verify all dependencies are installed

### Backend Won't Start on Railway?

Check these files in `api/` folder:

**Procfile**:
```
web: gunicorn server:app --bind 0.0.0.0:$PORT --log-level info
```

**runtime.txt**:
```
python-3.11.0
```

**requirements.txt** should include:
```
Flask==3.0.0
Flask-CORS==4.0.0
Werkzeug==3.0.1
gunicorn==21.2.0
aspose-words>=24.12.0
```

## Next Steps

After applying these fixes:

1. ✅ Push changes to GitHub
2. ✅ Railway will auto-deploy the backend changes
3. ✅ Add environment variable to Vercel
4. ✅ Redeploy frontend on Vercel
5. ✅ Test the complete flow

## Prevention

To prevent these issues in the future:

1. **Always test locally first** before deploying
2. **Use environment variables** for all API URLs
3. **Check CORS configuration** when adding new routes
4. **Monitor Railway logs** for backend errors
5. **Set up health checks** and monitoring
