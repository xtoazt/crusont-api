# Crusont API - Vercel Deployment Guide

This API has been configured to deploy on Vercel with consolidated serverless functions, multiple API key support, and a rustic frontend interface.

## 🚀 Deployment Steps

1. **Install Vercel CLI** (if not already installed):
   ```bash
   npm i -g vercel
   ```

2. **Login to Vercel**:
   ```bash
   vercel login
   ```

3. **Deploy the API**:
   ```bash
   vercel
   ```

4. **Set Environment Variables** (if needed):
   ```bash
   vercel env add DB_URL
   vercel env add OTHER_ENV_VAR
   ```

## 📁 Configuration Files

- `vercel.json` - Main Vercel configuration with frontend and docs routing
- `requirements.txt` - Python dependencies
- `api/index.py` - Vercel entry point
- `api/app/main_vercel.py` - Vercel-compatible FastAPI app
- `.vercelignore` - Files to exclude from deployment

## 🔗 API Endpoints

The consolidated API now has **8 serverless functions** instead of 12:

### Core Endpoints
1. `GET /` - Home endpoint with API information
2. `GET /v1/models` - List available models
3. `POST /v1/chat/completions` - Chat completions
4. `POST /v1/moderations` - Content moderation
5. `POST /v1/embeddings` - Text embeddings

### Consolidated Endpoints
6. `POST /v1/audio/speech` - Text-to-speech
7. `POST /v1/audio/transcriptions` - Speech-to-text
8. `POST /v1/audio/translations` - Audio translation
9. `POST /v1/images/generations` - Image generation
10. `POST /v1/images/upscale` - Image upscaling
11. `POST /v1/text/translations` - Text translation

### New API Key Management
12. `GET /v1/keys` - List user's API keys
13. `POST /v1/keys` - Create new API key
14. `DELETE /v1/keys/{key_id}` - Delete API key

## 🎨 Frontend & Documentation

- **Frontend**: `/` - Rustic API key management interface
- **Documentation**: `/docs/` - Comprehensive API documentation
- **API**: `/v1/*` - All API endpoints

## ✨ Key Features

### Multiple API Keys
- Users can create unlimited API keys
- Each key has a custom name
- Track usage per key
- One-click key management

### Rustic UI Design
- Medieval/tech aesthetic
- Responsive design
- Dark theme with golden accents
- Intuitive key management

### Comprehensive Documentation
- Complete API reference
- Code examples in multiple languages
- Pricing tiers and limits
- FAQ section

## 🔧 Key Changes for Vercel

- ✅ Removed background tasks and lifespan functions that don't work in serverless
- ✅ Created Vercel-compatible entry point
- ✅ Consolidated related endpoints into single files
- ✅ Added multiple API key support with database schema
- ✅ Created rustic frontend for key management
- ✅ Added comprehensive documentation
- ✅ Rebranded from Zukijourney to Crusont
- ✅ Removed OnlyFans tier references
- ✅ Added proper error handling for serverless environment
- ✅ Configured proper routing and build settings

## 🌐 Environment Variables

Make sure to set these environment variables in Vercel:

- `DB_URL` - MongoDB connection string
- Any other environment variables your app requires

## 🧪 Testing

After deployment, test the endpoints:

```bash
# Test home endpoint
curl https://your-app.vercel.app/

# Test models endpoint
curl https://your-app.vercel.app/v1/models

# Test API key creation (requires authentication)
curl -X POST https://your-app.vercel.app/v1/keys \
  -H "Authorization: Bearer your-api-key" \
  -H "Content-Type: application/json" \
  -d '{"name": "Test Key"}'
```

## 🎯 Access Points

- **Main Site**: `https://your-app.vercel.app/`
- **API Documentation**: `https://your-app.vercel.app/docs/`
- **API Endpoints**: `https://your-app.vercel.app/v1/*`
- **Key Management**: `https://your-app.vercel.app/` (frontend interface)

## 🔄 Migration Notes

- Old single API key system has been replaced with multiple keys
- Users will need to create new API keys through the web interface
- All branding has been updated from Zukijourney to Crusont
- OnlyFans tier has been removed from pricing structure
