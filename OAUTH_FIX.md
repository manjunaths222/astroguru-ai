# Fixing Google OAuth Redirect URI Mismatch Error

## Understanding the Setup

When using React dev server (port 3000) with backend (port 8002):

1. **OAuth Callback** (where Google redirects): Backend on port **8002**
2. **Frontend** (where users see the app): React dev server on port **3000**

## Current Issue

Your redirect URI needs to point to the **backend** (port 8002), not the React server (port 3000).

The OAuth callback endpoint is: `http://localhost:8002/api/v1/auth/google/callback`

## Quick Fix

### Step 1: Update Your .env File

Add or update these lines in your `.env` file:

```env
# OAuth callback goes to BACKEND (port 8002)
GOOGLE_REDIRECT_URI=http://localhost:8002/api/v1/auth/google/callback

# After OAuth, redirect to FRONTEND (port 3000 for React dev server)
FRONTEND_URL=http://localhost:3000
```

**Important:**
- `GOOGLE_REDIRECT_URI` = Backend callback endpoint (port 8002)
- `FRONTEND_URL` = React app URL (port 3000)

### Step 2: Update Google Cloud Console

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Navigate to **APIs & Services** > **Credentials**
3. Click on your OAuth 2.0 Client ID
4. Under **Authorized redirect URIs**, add:
   ```
   http://localhost:8002/api/v1/auth/google/callback
   ```
5. **Remove** the incorrect one (port 3000) if it exists
6. Click **Save**
7. Wait 1-2 minutes for changes to propagate

### Step 3: Update Authorized JavaScript Origins (Optional but Recommended)

In Google Cloud Console, also add the React dev server origin:

**Authorized JavaScript origins:**
```
http://localhost:3000
http://localhost:8002
```

This allows OAuth to work from both the React app and if you access the backend directly.

### Step 4: Restart Your Backend

After updating, restart your backend server:

```bash
cd /Users/yml/Documents/voltron/astroguru-ai-langgraph-repo/astroguru-ai
# Stop the current server (Ctrl+C)
# Then restart:
uvicorn main:app --reload
```

## Verify the Fix

Run these commands to verify your configuration:

```bash
cd /Users/yml/Documents/voltron/astroguru-ai-langgraph-repo/astroguru-ai
python -c "from config import AstroConfig; print('OAuth Redirect URI:', AstroConfig.AuthConfig.GOOGLE_REDIRECT_URI)"
python -c "import os; print('Frontend URL:', os.getenv('FRONTEND_URL', 'http://localhost:8002'))"
```

Expected output:
- OAuth Redirect URI: `http://localhost:8002/api/v1/auth/google/callback`
- Frontend URL: `http://localhost:3000` (if set in .env)

## How It Works

1. User clicks "Login with Google" in React app (port 3000)
2. React app calls backend API to get OAuth URL
3. User is redirected to Google for authentication
4. Google redirects back to **backend callback** (port 8002): `/api/v1/auth/google/callback`
5. Backend processes OAuth, creates JWT token
6. Backend redirects user to **React app** (port 3000): `/auth/callback?token=...`
7. React app receives token and stores it in localStorage

## Important Notes

- **OAuth Callback**: Always goes to backend (port 8002) - this is what Google needs
- **Frontend Redirect**: After OAuth, backend redirects to React app (port 3000)
- **Exact match required**: The redirect URI in Google Cloud Console must match EXACTLY
- **No trailing slash**: Don't add a trailing slash at the end
- **Both servers running**: Make sure both backend (8002) and React (3000) are running

## For Production

When deploying to production, update both:

1. **.env file**:
   ```env
   GOOGLE_REDIRECT_URI=https://yourdomain.com/api/v1/auth/google/callback
   ```

2. **Google Cloud Console**: Add the production redirect URI:
   ```
   https://yourdomain.com/api/v1/auth/google/callback
   ```

You can have multiple redirect URIs in Google Cloud Console (one for dev, one for prod).
