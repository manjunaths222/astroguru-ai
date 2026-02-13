"""FastAPI application for AstroGuru AI LangGraph"""

# CRITICAL: Initialize ChatGoogleGenerativeAI BEFORE importing any graph modules
# This resolves Pydantic v2 forward reference issues
# The import itself triggers the initialization
import utils.llm_init

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from contextlib import asynccontextmanager
from config import logger, AstroConfig
from graph.workflow import create_astroguru_graph
from graph.state import AstroGuruState
from services.email_service import send_analysis_email
import os
import asyncio


# Request/Response models
class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None  # For future session management
    email: Optional[str] = None  # Email address for sending report
    send_email: bool = False  # Flag to indicate if email should be sent


class ChatResponse(BaseModel):
    response: str
    analysis_complete: bool
    summary: Optional[str] = None
    chart_data_analysis: Optional[str] = None
    dasha_analysis: Optional[str] = None
    goal_analysis: Optional[str] = None
    recommendations: Optional[str] = None
    session_id: Optional[str] = None  # Return session_id for client to use in subsequent requests


# Global graph instance
_graph = None

# Simple in-memory session store (no persistence as requested)
_sessions: Dict[str, AstroGuruState] = {}


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup/shutdown"""
    global _graph
    logger.info("=" * 60)
    logger.info("Starting AstroGuru AI (LangGraph)...")
    logger.info("=" * 60)
    
    try:
        # Validate credentials
        logger.info("Validating Google AI API credentials...")
        if not AstroConfig.AppSettings.validate_google_credentials():
            logger.error("=" * 60)
            logger.error("CRITICAL: GOOGLE_AI_API_KEY not configured!")
            logger.error("Please set GOOGLE_AI_API_KEY in your environment or .env file")
            logger.error("=" * 60)
            raise ValueError("GOOGLE_AI_API_KEY not configured")
        
        logger.info("✓ Google AI API key found")
        
        # Create graph
        logger.info("Creating LangGraph workflow...")
        _graph = create_astroguru_graph()
        logger.info("=" * 60)
        logger.info("✓ AstroGuru LangGraph initialized successfully")
        logger.info("=" * 60)
        
    except ValueError as e:
        # Credential validation error
        logger.error("=" * 60)
        logger.error(f"CRITICAL ERROR: {e}")
        logger.error("Graph will not be available until GOOGLE_AI_API_KEY is configured")
        logger.error("=" * 60)
        _graph = None
    except Exception as e:
        logger.error("=" * 60)
        logger.error(f"Failed to initialize graph: {e}", exc_info=True)
        logger.error("Graph will not be available")
        logger.error("=" * 60)
        _graph = None
    
    yield
    
    logger.info("Shutting down AstroGuru AI...")


app = FastAPI(
    title=AstroConfig.AppSettings.APP_TITLE,
    description=AstroConfig.AppSettings.APP_DESCRIPTION,
    version=AstroConfig.AppSettings.VERSION,
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

# Mount static files
static_dir = os.path.join(os.path.dirname(__file__), "static")
if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")


@app.get("/")
async def read_root():
    """Serve the main web interface"""
    static_file = os.path.join(static_dir, "index.html")
    if os.path.exists(static_file):
        return FileResponse(static_file)
    return {"message": "AstroGuru AI API", "docs": "/docs"}


@app.get("/health")
async def health():
    """Health check endpoint"""
    logger.debug("Health check requested")
    health_status = {
        "status": "healthy" if _graph is not None else "degraded",
        "service": AstroConfig.AppSettings.APP_NAME,
        "graph_ready": _graph is not None,
    }
    if not _graph:
        health_status["error"] = "Graph not initialized - check GOOGLE_AI_API_KEY configuration"
    logger.info(f"Health check: {health_status}")
    return health_status


@app.get("/")
async def index():
    """Root endpoint"""
    return {
        "service": AstroConfig.AppSettings.APP_NAME,
        "version": AstroConfig.AppSettings.VERSION,
        "status": "running"
    }


@app.post("/api/v1/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Chat endpoint - handles both analysis workflow and post-analysis chat"""
    logger.info(f"Chat request received - session_id: {request.session_id}, message length: {len(request.message)}")
    
    if _graph is None:
        error_msg = "Graph not initialized. Please check server logs for initialization errors. " \
                   "Most likely cause: GOOGLE_AI_API_KEY not configured."
        logger.error("=" * 60)
        logger.error("Graph not initialized, returning 503")
        logger.error("Check startup logs above for initialization errors")
        logger.error("=" * 60)
        raise HTTPException(status_code=503, detail=error_msg)
    
    try:
        # Get or create session
        session_id = request.session_id or "default"
        logger.debug(f"Using session_id: {session_id}")
        
        # Get existing session state if available
        if session_id in _sessions:
            existing_state = _sessions[session_id]
            analysis_complete = existing_state.get('analysis_complete', False)
            existing_messages = existing_state.get('messages', [])
            logger.info(f"Found existing session: {session_id}, analysis_complete: {analysis_complete}, conversation history: {len(existing_messages)} messages")
            # Update with new message and clear request_type to let router decide
            # CRITICAL: Preserve all existing state including messages, birth_details, analysis_context, etc.
            initial_state: AstroGuruState = {
                **existing_state,
                "user_message": request.message,
                "request_type": None  # Clear to let router decide based on current state
            }
            # Explicitly ensure messages are preserved (defensive programming)
            if "messages" not in initial_state or not initial_state.get("messages"):
                initial_state["messages"] = existing_messages
                logger.warning(f"Messages were not preserved, restoring from existing state: {len(existing_messages)} messages")
        else:
            # Initialize new state
            logger.info(f"Creating new session: {session_id}")
            initial_state: AstroGuruState = {
                "user_message": request.message,
                "messages": [],
                "birth_details": None,
                "location_data": None,
                "chart_data": None,
                "dasha_data": None,
                "goal_analysis_data": None,
                "recommendation_data": None,
                "summary": None,
                "analysis_context": None,
                "current_step": None,
                "analysis_complete": False,
                "error": None,
                "request_type": None  # Let router decide
            }
        
        # Execute graph
        logger.info(f"Executing graph for session {session_id}, message preview: {request.message[:100]}...")
        result = await _graph.ainvoke(initial_state)
        logger.info(f"Graph execution completed for session {session_id}, current_step: {result.get('current_step')}, analysis_complete: {result.get('analysis_complete', False)}")
        
        # Store updated state in session
        _sessions[session_id] = result
        logger.debug(f"Session state updated for {session_id}")
        
        # Extract response
        messages = result.get("messages", [])
        logger.debug(f"Total messages in session: {len(messages)}")
        
        if messages:
            # Get the last assistant message
            last_assistant_msg = None
            for msg in reversed(messages):
                if msg.get("role") == "assistant":
                    last_assistant_msg = msg.get("content", "")
                    break
            
            response_text = last_assistant_msg or "I apologize, but I couldn't generate a response."
            logger.debug(f"Response text length: {len(response_text)}")
        else:
            logger.warning("No messages found in result, using default response")
            response_text = "I apologize, but I couldn't generate a response."
        
        analysis_complete = result.get("analysis_complete", False)
        summary = result.get("summary")
        
        # Extract all analysis data from the result
        chart_data_analysis = result.get("chart_data_analysis")
        dasha_analysis = None
        goal_analysis = None
        recommendations = None
        
        # Get dasha analysis if available
        dasha_data = result.get("dasha_data")
        if dasha_data:
            dasha_analysis = dasha_data.get("analysis")
        
        # Get goal analysis if available
        goal_analysis_data = result.get("goal_analysis_data")
        if goal_analysis_data:
            goal_analysis = goal_analysis_data.get("analysis")
        
        # Get recommendations if available
        recommendation_data = result.get("recommendation_data")
        if recommendation_data:
            recommendations = recommendation_data.get("recommendations")
        
        logger.info(f"Chat response prepared - analysis_complete: {analysis_complete}, summary_length: {len(summary) if summary else 0}, chart_analysis: {bool(chart_data_analysis)}, dasha_analysis: {bool(dasha_analysis)}, goal_analysis: {bool(goal_analysis)}, recommendations: {bool(recommendations)}")
        
        # Send email if requested and analysis is complete
        if analysis_complete and request.send_email and request.email and summary:
            birth_details = result.get("birth_details")
            user_name = birth_details.get('name', 'User') if birth_details else 'User'
            
            # Send email asynchronously (don't block response)
            asyncio.create_task(
                send_analysis_email(
                    email=request.email,
                    name=user_name,
                    summary=summary,
                    chart_analysis=chart_data_analysis,
                    dasha_analysis=dasha_analysis,
                    goal_analysis=goal_analysis,
                    recommendations=recommendations
                )
            )
            logger.info(f"Email sending task created for {request.email} (user: {user_name})")
        
        return ChatResponse(
            response=response_text,
            analysis_complete=analysis_complete,
            summary=summary,
            chart_data_analysis=chart_data_analysis,
            dasha_analysis=dasha_analysis,
            goal_analysis=goal_analysis,
            recommendations=recommendations,
            session_id=session_id
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing chat request for session {request.session_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error processing request: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    import os
    # Use PORT from environment (Render sets this) or fallback to config
    port = int(os.getenv("PORT", AstroConfig.AppSettings.PORT))
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        reload=AstroConfig.AppSettings.DEBUG
    )

