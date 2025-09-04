# 🧪 Crusont API Testing Guide

## Quick Test URLs

Once deployed, test these URLs to verify everything works:

### Core API Endpoints
- `https://your-domain.vercel.app/` - Root endpoint
- `https://your-domain.vercel.app/health` - Health check
- `https://your-domain.vercel.app/test` - Test endpoint
- `https://your-domain.vercel.app/v1/models` - Models list

### Static Files
- `https://your-domain.vercel.app/favicon.ico` - Favicon
- `https://your-domain.vercel.app/robots.txt` - Robots.txt
- `https://your-domain.vercel.app/sitemap.xml` - Sitemap
- `https://your-domain.vercel.app/manifest.json` - Manifest
- `https://your-domain.vercel.app/styles.css` - CSS fallback
- `https://your-domain.vercel.app/script.js` - JS fallback

### Frontend
- `https://your-domain.vercel.app/` - Main frontend
- `https://your-domain.vercel.app/test.html` - Test page

## Expected Results

All endpoints should return:
- ✅ **Status 200** - Success
- ✅ **Valid JSON** (for API endpoints)
- ✅ **No 404 errors** in browser console

## Debugging

If you see 404 errors:
1. Check the Vercel deployment logs
2. Visit `/test.html` to run automated tests
3. Check browser developer tools console
4. Verify all files are in the repository

## Test Commands

```bash
# Test locally (if you have the API running)
python test_api.py

# Check file structure
ls -la frontend/
ls -la api/app/
```

## Common Issues Fixed

- ✅ Favicon 404 errors
- ✅ Static file loading issues
- ✅ Missing endpoints
- ✅ Routing configuration problems
- ✅ CORS issues
