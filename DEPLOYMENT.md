# Deployment Guide - Render.com

This guide covers deploying the AstroGuru AI LangGraph API to Render.com.

## Prerequisites

1. **GitHub Account** - Your code should be in a GitHub repository
2. **Render Account** - Sign up at [render.com](https://render.com) (free with GitHub)
3. **API Keys**:
   - `GOOGLE_AI_API_KEY` - Get from [Google AI Studio](https://makersuite.google.com/app/apikey)

## Render Free Tier

**Free Tier Includes:**
- 750 hours/month of free compute time
- Automatic SSL certificates
- Custom domains
- Auto-deploy from GitHub

**Note:** Free tier services spin down after 15 minutes of inactivity. First request after spin-down may take 30-60 seconds.

## Deployment Steps

### Step 1: Deploy Web Service

1. Go to [Render Dashboard](https://dashboard.render.com)
2. Click **"New"** → **"Web Service"**
3. **Connect GitHub**:
   - Click "Connect GitHub" if not already connected
   - Authorize Render to access your repositories
   - Select the `astroguru-ai-langgraph` repository
4. **Configure Service**:
   - **Name**: `astroguru-ai-langgraph`
   - **Region**: Choose closest to you (e.g., Oregon, Frankfurt)
   - **Branch**: `main` (or your default branch)
   - **Root Directory**: Leave empty
   - **Environment**: `Docker`
   - **Dockerfile Path**: `Dockerfile`
   - **Docker Context**: `.`

### Step 2: Set Environment Variables

1. In your Web Service settings, go to **"Environment"** tab
2. Add the following environment variables:

   **Required:**
   ```
   GOOGLE_AI_API_KEY=<your-google-ai-api-key>
   ```

   **Optional (with defaults):**
   ```
   PORT=8002
   GEMINI_MODEL=gemini-2.0-flash-exp
   GEMINI_TEMPERATURE=0.2
   GEMINI_MAX_TOKENS=8192
   DEBUG=false
   ENV=production
   ```

   **To get GOOGLE_AI_API_KEY:**
   1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
   2. Sign in with your Google account
   3. Click "Create API Key"
   4. Copy the API key and paste it as `GOOGLE_AI_API_KEY` value

### Step 3: Deploy

1. Click **"Create Web Service"**
2. Render will:
   - Build your Docker image
   - Deploy the service
   - Show build logs in real-time
3. Once deployed, your API will be available at:
   ```
   https://astroguru-ai-langgraph.onrender.com
   ```

## Using render.yaml (Alternative Method)

If you prefer to use `render.yaml` for configuration:

1. The `render.yaml` file is already in the repository
2. When creating a new service, Render will automatically detect and use it
3. You still need to set `GOOGLE_AI_API_KEY` manually in the Render dashboard (marked as `sync: false`)

## Post-Deployment

### 1. Verify Deployment

Check that the service is running:

```bash
curl https://astroguru-ai-langgraph.onrender.com/health
```

Expected response:
```json
{
  "status": "healthy",
  "service": "astroguru-ai-langgraph",
  "graph_ready": true
}
```

### 2. Test the Chat Endpoint

```bash
curl -X POST "https://astroguru-ai-langgraph.onrender.com/api/v1/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Hi, I would like to get my horoscope analyzed"
  }'
```

### 3. Monitor Logs

- Go to your service in Render Dashboard
- Click on **"Logs"** tab to see real-time logs
- Check for any errors or warnings

## Environment Variables Reference

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `GOOGLE_AI_API_KEY` | Yes | - | Google AI API key for Gemini models |
| `PORT` | No | 8002 | Port number for the server |
| `GEMINI_MODEL` | No | gemini-2.0-flash-exp | Gemini model to use |
| `GEMINI_TEMPERATURE` | No | 0.2 | Temperature for model responses |
| `GEMINI_MAX_TOKENS` | No | 8192 | Maximum tokens for responses |
| `DEBUG` | No | false | Enable debug mode |
| `ENV` | No | production | Environment name |

## Troubleshooting

### Service Won't Start

1. **Check Logs**: Go to Render Dashboard → Your Service → Logs
2. **Common Issues**:
   - Missing `GOOGLE_AI_API_KEY`: Check environment variables
   - Port conflicts: Ensure PORT is set correctly
   - Build failures: Check Dockerfile and requirements.txt

### Slow First Request

- Free tier services spin down after inactivity
- First request after spin-down takes 30-60 seconds to wake up
- Consider upgrading to paid tier for always-on service

### API Key Issues

- Verify API key is correct in Render dashboard
- Check API key has proper permissions
- Ensure no extra spaces or quotes in the API key value

## Upgrading to Paid Tier

For production use, consider upgrading to paid tier:
- **Starter Plan**: $7/month - Always-on service, no spin-down
- **Standard Plan**: $25/month - More resources, better performance

## Continuous Deployment

Render automatically deploys when you push to your connected branch:
1. Push changes to GitHub
2. Render detects the push
3. Builds new Docker image
4. Deploys automatically
5. Sends email notification on completion

## Custom Domain

1. Go to your service settings
2. Click **"Custom Domains"**
3. Add your domain
4. Follow DNS configuration instructions
5. SSL certificate is automatically provisioned

