# Vercel Environment Variables Setup

## Required Environment Variables

To fix CORS and ensure the backend works, add these in Vercel:

### 1. Go to Vercel Dashboard
- Navigate to your `codeshield-backend` project
- Click **Settings** → **Environment Variables**

### 2. Add These Variables

#### Required:
```
GEMINI_API_KEY=your_google_gemini_api_key_here
```

#### Optional (for CORS):
```
CORS_ORIGINS=http://localhost:3000,http://localhost:5173,https://your-frontend-domain.vercel.app
```

#### Optional (for Database - if using):
```
DATABASE_URL=your_postgresql_connection_string
```

### 3. Redeploy
After adding environment variables, Vercel will automatically redeploy, or you can manually trigger a redeploy.

## Quick Setup Steps

1. **Get Gemini API Key**:
   - Go to https://makersuite.google.com/app/apikey
   - Create a new API key
   - Copy it

2. **Add to Vercel**:
   - Vercel Dashboard → Project → Settings → Environment Variables
   - Add `GEMINI_API_KEY` with your key
   - Add `CORS_ORIGINS` with your frontend URLs (optional, code now allows all origins)

3. **Redeploy**:
   - Go to Deployments tab
   - Click "Redeploy" on the latest deployment

## Testing

After redeploying, test the endpoint:
```
https://codeshield-backend-alno3erkd-taha-kotwals-projects.vercel.app/health
```

You should get a JSON response with health status.

## Current CORS Configuration

The backend now:
- **Allows all origins** in development/Vercel (for easier testing)
- Can be restricted using `CORS_ORIGINS` environment variable if needed

This should fix CORS issues immediately!

