# AstroGuru AI - LangGraph Version

An AI-powered astrology analysis system using **LangGraph** and **Gemini Models** to provide comprehensive horoscope analysis, chart generation, Dasha reports, and goal-oriented forecasts.

## Features

The system provides comprehensive astrology analysis including:

1. **Intelligent Routing**: Automatically determines if user wants analysis or general chat
2. **Chart Generation**: Generates Lagna and Divisional charts in South Indian style
3. **Dasha Analysis**: Generates lifetime and on-demand Dasha/Bhukthi reports
4. **Goal-Oriented Analysis**: Detailed analysis and forecasts for specific goals (career, marriage, love life, etc.)
5. **Recommendations**: Provides detailed recommendations and remedies based on analysis
6. **Location Resolution**: Automatically resolves place names to geographic coordinates using geocoding API
7. **Chat with Context**: After analysis is complete, supports normal chat conversations with full context from the analysis
8. **Timezone Correction**: Automatically validates and corrects timezone information
9. **Email Reports**: Optional email delivery of complete astrology reports (users can choose to receive reports via email instead of waiting on screen)

## Prerequisites

1. **Python 3.11 or higher**
2. **Google AI API Key** (for Gemini models)
   - Get your API key from [Google AI Studio](https://makersuite.google.com/app/apikey)

## Installation

### Step 1: Clone/Navigate to the Project

```bash
cd /Users/yml/Documents/voltron/astroguru-ai-langgraph
```

### Step 2: Create Virtual Environment

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate

# On Windows:
venv\Scripts\activate
```

### Step 3: Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### Step 4: Configure Environment Variables

Create a `.env` file in the project root:

```bash
# Create .env file
touch .env
```

Add the following to `.env`:

```env
# Required: Google AI API Key
GOOGLE_AI_API_KEY=your-google-ai-api-key-here

# Optional: Gemini Model Configuration
GEMINI_MODEL=gemini-2.0-flash-exp
GEMINI_TEMPERATURE=0.2
GEMINI_MAX_TOKENS=8192

# Optional: Server Configuration
PORT=8002
DEBUG=false
ENV=dev

# Optional: Email Configuration (for sending reports via email using Resend)
RESEND_API_KEY=re_your_api_key_here
RESEND_FROM_EMAIL=onboarding@resend.dev
RESEND_FROM_NAME=AstroGuru AI
```

**Important**: 
- Replace `your-google-ai-api-key-here` with your actual Google AI API key.
- For email functionality, get your Resend API key from [https://resend.com/api-keys](https://resend.com/api-keys) and verify your domain at [https://resend.com/domains](https://resend.com/domains). The free tier includes 3,000 emails/month.

Alternatively, you can set environment variables directly:

```bash
export GOOGLE_AI_API_KEY="your-google-ai-api-key-here"
```

## Running the Application

### Start the FastAPI Server

```bash
# Make sure virtual environment is activated
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Start the server
uvicorn main:app --reload --host 0.0.0.0 --port 8002
```

The `--reload` flag enables auto-reload on code changes (useful for development).

**Access the API:**
- **API Documentation (Swagger UI)**: http://localhost:8002/docs
- **Alternative API Docs (ReDoc)**: http://localhost:8002/redoc
- **Health Check**: http://localhost:8002/health
- **Root**: http://localhost:8002/

## API Endpoints

### Health Check

**Endpoint**: `GET /health`

**Description**: Check service health and graph availability

**Response**:
```json
{
  "status": "healthy",
  "graph_initialized": true,
  "version": "2.0.0"
}
```

### Chat Endpoint

**Endpoint**: `POST /api/v1/chat`

**Description**: Main endpoint for interacting with the astrology system. Supports both analysis requests and general chat.

**Request Body**:
```json
{
  "message": "Hi, I'd like to get my horoscope analyzed",
  "session_id": "optional-session-id",
  "email": "user@example.com",
  "send_email": true
}
```

**Email Fields** (optional):
- `email`: Email address to send the report to
- `send_email`: Boolean flag to enable email delivery (default: `false`)

**Response**:
```json
{
  "response": "Hello! I'm a Vedic Astrology Consultant...",
  "analysis_complete": false,
  "summary": null,
  "session_id": "session-id-here"
}
```

**Example Requests**:

1. **Start Analysis**:
```json
{
  "message": "I want my horoscope analyzed",
  "session_id": "user-123"
}
```

2. **General Chat**:
```json
{
  "message": "What is Vedic astrology?",
  "session_id": "user-123"
}
```

3. **Follow-up After Analysis**:
```json
{
  "message": "What does my chart say about my career?",
  "session_id": "user-123"
}
```

## Usage Flow

### 1. Analysis Flow

1. **Start Conversation**: Send a greeting or request for horoscope analysis
   ```
   "Hi, I'd like to get my horoscope analyzed"
   ```

2. **Provide Birth Details**: The system will ask for:
   - **Name**: Full name
   - **Date of Birth**: YYYY-MM-DD format (e.g., "1990-05-15")
   - **Time of Birth**: HH:MM format, 24-hour (e.g., "14:30")
   - **Place of Birth**: City, state, country (e.g., "Mumbai, Maharashtra, India")
   - **Goals** (optional): career, marriage, love life, health, education, finance, etc.

3. **Automatic Processing**: The system will automatically:
   - Resolve location coordinates using geocoding API
   - Validate and correct timezone
   - Generate birth chart using jyotishganit
   - Calculate Dasha periods
   - Analyze goals
   - Generate recommendations
   - Create comprehensive summary

4. **Email Delivery** (Optional): Users can choose to receive the report via email:
   - Check the "Send report to my email" checkbox
   - Enter email address
   - Report will be sent automatically when analysis completes
   - Report is also displayed on screen for immediate viewing

5. **Chat with Context**: After analysis is complete, you can ask questions:
   ```
   "What does my chart say about my career?"
   "Tell me about my current Dasha period"
   "What are the recommendations for my marriage?"
   ```

### 2. General Chat Flow

The system can also handle general astrology questions without requiring analysis:

```
"What is Vedic astrology?"
"Explain planetary positions"
"Tell me about nakshatras"
```

The router automatically determines whether to perform analysis or handle general chat.

## Architecture

The system uses **LangGraph** for workflow orchestration with specialized nodes:

### Workflow Nodes

1. **Router Node**: Entry point that determines if user wants analysis or general chat
2. **Main Node**: Collects birth details from user conversation
3. **Location Node**: Resolves geographic coordinates using geocoding API with agent-based validation
4. **Chart Node**: Generates Vedic astrology charts using jyotishganit
5. **Dasha Node**: Calculates and analyzes Vimshottari Dasha periods
6. **Goal Analysis Node**: Analyzes horoscope for specific life goals
7. **Recommendation Node**: Provides recommendations and remedies
8. **Summarizer Node**: Combines all analysis into a comprehensive report
9. **Chat Node**: Handles normal chat with context after analysis

### Workflow Graph

```
Router
  ├─→ Chat (for general questions)
  └─→ Analysis Flow:
       Main → Location → Chart → Dasha → Goal Analysis → Recommendation → Summarizer
                                                                    ↓
                                                              Chat (with context)
```

### State Management

The system uses `AstroGuruState` (TypedDict) to manage conversation state:
- User messages and conversation history
- Birth details and location data
- Chart, Dasha, and analysis data
- Summary and analysis context
- Request type (chat/analysis)

### Key Features

- **Optimized Chart Calculation**: Chart is calculated once and reused across all operations
- **Agent-Based Location Resolution**: Uses LLM agent with geocoding tools for accurate location resolution
- **Timezone Validation**: Automatically validates and corrects timezone information
- **In-Memory Sessions**: Simple session management without persistence
- **Intelligent Routing**: Automatically routes between chat and analysis based on user intent

## Configuration

### Required Environment Variables

- `GOOGLE_AI_API_KEY`: Google AI API key for Gemini models (required)

### Optional Environment Variables

- `GEMINI_MODEL`: Gemini model to use (default: `"gemini-2.0-flash-exp"`)
- `GEMINI_TEMPERATURE`: Temperature for model (default: `0.2`)
- `GEMINI_MAX_TOKENS`: Maximum tokens (default: `8192`)
- `PORT`: Server port (default: `8002`)
- `DEBUG`: Enable debug mode (default: `false`)
- `ENV`: Environment name (default: `dev`)

### Email Configuration (Optional)

To enable email delivery of reports, configure Resend settings:

- `RESEND_API_KEY`: Your Resend API key (required for email functionality)
- `RESEND_FROM_EMAIL`: From email address (must be a verified domain in Resend)
- `RESEND_FROM_NAME`: From name (default: `"AstroGuru AI"`)

**Resend Setup**:
1. Sign up at [https://resend.com](https://resend.com)
2. Get your API key from [https://resend.com/api-keys](https://resend.com/api-keys)
3. Verify your domain at [https://resend.com/domains](https://resend.com/domains)
   - For testing, you can use `onboarding@resend.dev` (Resend's test domain)
   - For production, verify your own domain
4. Set `RESEND_API_KEY` in your `.env` file

**Resend Free Tier**:
- 3,000 emails/month
- 100 emails/day
- Perfect for development and small-scale production

**Benefits of Resend**:
- Simple API (no SMTP configuration needed)
- Better deliverability
- Email tracking and analytics
- Webhook support for delivery events

## Deployment

The application is configured for deployment on **Render.com** using Docker.

### Quick Deploy to Render.com

1. **Push code to GitHub** (or GitLab/Bitbucket)

2. **Create new Web Service on Render**:
   - Connect your repository
   - Select "Docker" as the runtime
   - Set build command: (leave empty, uses Dockerfile)
   - Set start command: (leave empty, uses Dockerfile CMD)

3. **Set Environment Variables**:
   - `GOOGLE_AI_API_KEY`: Your Google AI API key
   - `PORT`: 8002 (or let Render set it automatically)
   - `GEMINI_MODEL`: gemini-2.0-flash-exp (optional)
   - `GEMINI_TEMPERATURE`: 0.2 (optional)
   - `GEMINI_MAX_TOKENS`: 8192 (optional)
   - `RESEND_API_KEY`, `RESEND_FROM_EMAIL`: For email functionality (optional)

4. **Deploy**: Render will automatically build and deploy your application

See [DEPLOYMENT.md](DEPLOYMENT.md) for detailed deployment instructions.

## Testing

### Test the API with curl

```bash
# Health check
curl http://localhost:8002/health

# Start a chat
curl -X POST http://localhost:8002/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Hi, I want my horoscope analyzed",
    "session_id": "test-123"
  }'
```

### Test with Python

```python
import requests

# Health check
response = requests.get("http://localhost:8002/health")
print(response.json())

# Chat
response = requests.post(
    "http://localhost:8002/api/v1/chat",
    json={
        "message": "Hi, I want my horoscope analyzed",
        "session_id": "test-123"
    }
)
print(response.json())
```

## Troubleshooting

### 1. Graph Not Initialized

**Error**: `Graph not initialized` or `GOOGLE_AI_API_KEY not configured`

**Solution**:
- Verify `GOOGLE_AI_API_KEY` is set in `.env` file or environment variables
- Check the key is valid and has proper permissions
- Restart the server after setting the key

### 2. Chart Generation Fails

**Error**: Chart calculation errors or missing data

**Solution**:
- Verify birth details are complete and valid
- Check date format is YYYY-MM-DD
- Check time format is HH:MM (24-hour)
- Ensure jyotishganit is installed correctly: `pip install jyotishganit`

### 3. Location Resolution Fails

**Error**: `Failed to resolve location` or geocoding errors

**Solution**:
- Ensure place name is specific (include city, state, country)
- Check internet connection (geocoding uses external API)
- Verify geocoding API is accessible (Nominatim/OpenStreetMap)

### 4. Timezone Issues

**Error**: Invalid timezone or timezone not found

**Solution**:
- The system automatically corrects timezone from coordinates
- The code has a built-in fallback timezone lookup (doesn't require timezonefinder)
- Optional: Install `timezonefinder` for more accurate timezone detection: `pip install timezonefinder` (requires build tools for h3 dependency)
- Check coordinates are valid

### 5. Import Errors

**Error**: `ModuleNotFoundError` or import errors

**Solution**:
- Ensure virtual environment is activated
- Reinstall dependencies: `pip install -r requirements.txt`
- Check Python version: `python --version` (should be 3.11+)

### 6. Port Already in Use

**Error**: `Address already in use` on port 8002

**Solution**:
- Change port in `.env`: `PORT=8003`
- Or kill the process using the port:
  ```bash
  # Find process
  lsof -i :8002
  # Kill process
  kill -9 <PID>
  ```

## Differences from ADK Version

1. **Framework**: Uses LangGraph instead of Google ADK
2. **Models**: Uses Gemini API directly via `langchain-google-genai`
3. **Workflow**: Explicit graph-based workflow instead of SequentialAgent
4. **Chat Support**: Built-in chat node for post-analysis conversations
5. **State Management**: Explicit state management with TypedDict
6. **Location Resolution**: Uses geocoding API with agent-based validation
7. **No Persistence**: Simple API without database (as requested)
8. **Intelligent Routing**: Router node automatically determines user intent

## Project Structure

```
astroguru-ai-langgraph/
├── config.py                 # Configuration and settings
├── main.py                   # FastAPI application entry point
├── requirements.txt          # Python dependencies
├── Dockerfile                # Docker configuration for deployment
├── render.yaml               # Render.com deployment configuration
├── DEPLOYMENT.md             # Detailed deployment instructions
├── graph/
│   ├── __init__.py
│   ├── state.py              # AstroGuruState TypedDict
│   ├── workflow.py           # LangGraph workflow definition
│   └── nodes/
│       ├── __init__.py
│       ├── router_node.py    # Router for chat/analysis decision
│       ├── main_node.py       # Birth details collection
│       ├── location_node.py   # Location resolution with agent
│       ├── chart_node.py      # Chart generation
│       ├── dasha_node.py      # Dasha calculations
│       ├── goal_analysis_node.py  # Goal analysis
│       ├── recommendation_node.py # Recommendations
│       ├── summarizer_node.py     # Summary generation
│       └── chat_node.py           # Chat with context
├── services/
│   ├── __init__.py
│   └── email_service.py      # Email service for sending reports
└── tools/
    ├── __init__.py
    ├── geocoding_tools.py    # Geocoding API tools
    └── vedastro_tools.py      # Astrology calculation tools
```

## License

Same as original astroguru-ai project.

## Support

For issues or questions, please check the troubleshooting section or review the code documentation.
