"""FastAPI application for AstroGuru AI LangGraph"""

# CRITICAL: Initialize ChatGoogleGenerativeAI BEFORE importing any graph modules
# This resolves Pydantic v2 forward reference issues
# The import itself triggers the initialization
import utils.llm_init

from fastapi import FastAPI, HTTPException, Depends, status, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, RedirectResponse, JSONResponse
from pydantic import BaseModel, EmailStr
from typing import Optional, List, Dict, Any
from contextlib import asynccontextmanager
from sqlalchemy.orm import Session
from datetime import datetime
import os
import asyncio
import json

from config import logger, AstroConfig
from database import init_database, close_database, get_db
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from graph.workflow import create_astroguru_graph
from graph.state import AstroGuruState
from services.email_service import send_analysis_email
from services.payment_service import payment_service
from services.order_service import order_service
from auth.oauth import get_google_oauth_url, handle_google_callback
from auth.admin_auth import verify_admin_credentials, get_password_hash
from auth.jwt_handler import create_access_token
from auth.dependencies import get_current_user_dependency, get_current_admin, get_optional_user
from models.user import User
from models.order import Order
from models.payment import Payment
from sqlalchemy import select


# Request/Response models
class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None
    email: Optional[str] = None
    send_email: bool = False


class ChatResponse(BaseModel):
    response: str
    analysis_complete: bool
    summary: Optional[str] = None
    chart_data_analysis: Optional[str] = None
    dasha_analysis: Optional[str] = None
    goal_analysis: Optional[str] = None
    recommendations: Optional[str] = None
    session_id: Optional[str] = None


class OrderCreateRequest(BaseModel):
    birth_details: Dict[str, Any]
    order_type: str = "full_report"  # "full_report" or "query"
    user_query: Optional[str] = None  # Required if order_type is "query"


class OrderResponse(BaseModel):
    id: int
    user_id: int
    status: str
    type: str
    amount: float
    birth_details: Optional[Dict] = None
    analysis_data: Optional[Dict] = None
    error_reason: Optional[str] = None
    created_at: datetime
    updated_at: datetime


class PaymentCreateResponse(BaseModel):
    order_id: int
    razorpay_order_id: str
    amount: float
    key_id: str
    currency: str = "INR"


class PaymentVerifyRequest(BaseModel):
    razorpay_order_id: str
    razorpay_payment_id: str
    razorpay_signature: str


class AdminLoginRequest(BaseModel):
    email: str
    password: str


class AdminLoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_type: str = "admin"


# Global graph instance
_graph = None

# Simple in-memory session store (for graph execution)
_sessions: Dict[str, AstroGuruState] = {}
_scheduler = None


def check_stale_processing_orders():
    """Cron job to check and mark stale processing orders as failed"""
    from database import SessionLocal
    
    stale_threshold_minutes = 30  # Mark orders as failed after 30 minutes
    
    db = SessionLocal()
    try:
        # Get stale processing orders
        stale_orders = order_service.get_stale_processing_orders(
            db, minutes_threshold=stale_threshold_minutes
        )
        
        if stale_orders:
            logger.info(f"Found {len(stale_orders)} stale processing order(s)")
            
            for order in stale_orders:
                # Calculate how long it's been processing
                time_elapsed = datetime.utcnow() - order.created_at
                minutes_elapsed = int(time_elapsed.total_seconds() / 60)
                
                error_reason = f"Order stuck in processing status for {minutes_elapsed} minutes (threshold: {stale_threshold_minutes} minutes)"
                
                # Mark as failed
                order_service.fail_order(
                    db, 
                    order.id, 
                    error_reason
                )
                
                logger.warning(
                    f"Marked order {order.id} as failed: {error_reason}"
                )
            
            db.commit()
        else:
            logger.debug("No stale processing orders found")
            
    except Exception as e:
        logger.error(f"Error checking stale orders: {e}", exc_info=True)
        db.rollback()
    finally:
        db.close()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup/shutdown"""
    global _graph
    logger.info("=" * 60)
    logger.info("Starting AstroGuru AI (LangGraph)...")
    logger.info("=" * 60)
    
    try:
        # Initialize database
        logger.info("Initializing database...")
        init_database()
        logger.info("✓ Database initialized")
        
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
        logger.error("=" * 60)
        logger.error(f"CRITICAL ERROR: {e}")
        logger.error("Graph will not be available until GOOGLE_AI_API_KEY is configured")
        logger.error("=" * 60)
        _graph = None
    except Exception as e:
        logger.error("=" * 60)
        logger.error(f"Failed to initialize: {e}", exc_info=True)
        logger.error("=" * 60)
        _graph = None
    
    # Start APScheduler for cron jobs
    global _scheduler
    try:
        logger.info("Starting APScheduler for cron jobs...")
        _scheduler = AsyncIOScheduler()
        
        # Add cron job to check stale processing orders every 5 minutes
        _scheduler.add_job(
            check_stale_processing_orders,
            trigger=IntervalTrigger(minutes=5),
            id='check_stale_orders',
            name='Check stale processing orders',
            replace_existing=True
        )
        
        _scheduler.start()
        logger.info("✓ APScheduler started - stale order check scheduled every 5 minutes")
        
        # Run initial check immediately
        logger.info("Running initial stale order check...")
        check_stale_processing_orders()
        
    except Exception as e:
        logger.error(f"Failed to start APScheduler: {e}", exc_info=True)
        _scheduler = None
    
    yield
    
    # Shutdown
    logger.info("Shutting down AstroGuru AI...")
    
    # Stop scheduler
    if _scheduler:
        logger.info("Stopping APScheduler...")
        _scheduler.shutdown(wait=False)
        logger.info("✓ APScheduler stopped")
    
    close_database()


app = FastAPI(
    title=AstroConfig.AppSettings.APP_TITLE,
    description=AstroConfig.AppSettings.APP_DESCRIPTION,
    version=AstroConfig.AppSettings.VERSION,
    lifespan=lifespan
)

# CORS Configuration
cors_origins = AstroConfig.CORSConfig.CORS_ORIGINS
if cors_origins == ["*"]:
    logger.warning("CORS is set to allow all origins (*). This should only be used in development!")
else:
    logger.info(f"CORS configured for origins: {cors_origins}")

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=AstroConfig.CORSConfig.CORS_ALLOW_CREDENTIALS,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=["*"],
    expose_headers=["*"]
)

# Mount static files (for legacy support)
static_dir = os.path.join(os.path.dirname(__file__), "static")
if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")

# Mount React build (production)
react_build_dir = os.path.join(os.path.dirname(__file__), "frontend", "dist")
react_build_exists = os.path.exists(react_build_dir)

if react_build_exists:
    # Mount React assets
    app.mount("/assets", StaticFiles(directory=os.path.join(react_build_dir, "assets")), name="assets")
    logger.info("React build found - serving React application")
else:
    logger.info("React build not found - serving legacy static files")


@app.get("/")
async def read_root():
    """Serve the main web interface - React app if available, else legacy"""
    # Try React build first
    if react_build_exists:
        react_index = os.path.join(react_build_dir, "index.html")
        if os.path.exists(react_index):
            return FileResponse(react_index)
    
    # Fallback to legacy static files
    static_file = os.path.join(static_dir, "index.html")
    if os.path.exists(static_file):
        return FileResponse(static_file)
    return {"message": "AstroGuru AI API", "docs": "/docs"}


@app.get("/auth/callback")
async def auth_callback():
    """OAuth callback handler - serves React app or legacy index.html"""
    # Try React build first
    if react_build_exists:
        react_index = os.path.join(react_build_dir, "index.html")
        if os.path.exists(react_index):
            return FileResponse(react_index)
    
    # Fallback to legacy
    static_file = os.path.join(static_dir, "index.html")
    if os.path.exists(static_file):
        return FileResponse(static_file)
    return {"message": "Auth callback - token should be in URL"}


@app.get("/health")
async def health():
    """Health check endpoint"""
    health_status = {
        "status": "healthy" if _graph is not None else "degraded",
        "service": AstroConfig.AppSettings.APP_NAME,
        "graph_ready": _graph is not None,
    }
    if not _graph:
        health_status["error"] = "Graph not initialized - check GOOGLE_AI_API_KEY configuration"
    return health_status


# ==================== Authentication Endpoints ====================

@app.get("/api/v1/auth/google")
async def google_oauth_initiate():
    """Initiate Google OAuth flow"""
    try:
        auth_url = await get_google_oauth_url()
        return {"auth_url": auth_url}
    except Exception as e:
        logger.error(f"Error generating OAuth URL: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to initiate OAuth")


@app.get("/api/v1/auth/google/callback")
async def google_oauth_callback(code: str, db: Session = Depends(get_db)):
    """Handle Google OAuth callback"""
    try:
        result = await handle_google_callback(code, db)
        # Redirect to frontend with token
        frontend_url = os.getenv("FRONTEND_URL", "http://localhost:8002")
        redirect_url = f"{frontend_url}/auth/callback?token={result['access_token']}"
        return RedirectResponse(url=redirect_url)
    except ValueError as e:
        logger.error(f"OAuth callback error: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error handling OAuth callback: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Authentication failed")


@app.post("/api/v1/auth/admin/login", response_model=AdminLoginResponse)
async def admin_login(request: AdminLoginRequest):
    """Admin login endpoint"""
    try:
        if verify_admin_credentials(request.email, request.password):
            token_data = {
                "sub": "0",  # Admin ID (JWT 'sub' must be a string)
                "email": request.email,
                "type": "admin"
            }
            access_token = create_access_token(token_data)
            return AdminLoginResponse(access_token=access_token)
        else:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials"
            )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Admin login error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Login failed")


@app.get("/api/v1/auth/me")
async def get_current_user_info(
    current_user: dict = Depends(get_current_user_dependency),
    db: Session = Depends(get_db)
):
    """Get current user information"""
    if current_user.get("user_type") == "admin":
        return {
            "id": 0,
            "email": current_user.get("email"),
            "type": "admin"
        }
    
    # Get user from database
    stmt = select(User).where(User.id == current_user["user_id"])
    result = db.execute(stmt)
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return {
        "id": user.id,
        "email": user.email,
        "name": user.name,
        "picture_url": user.picture_url,
        "type": "user"
    }


# ==================== Order Endpoints ====================

@app.post("/api/v1/orders", response_model=OrderResponse)
async def create_order(
    request: OrderCreateRequest,
    current_user: dict = Depends(get_current_user_dependency),
    db: Session = Depends(get_db)
):
    """Create a new order"""
    try:
        # Validate order_type
        if request.order_type not in ["full_report", "query"]:
            raise HTTPException(status_code=400, detail="Invalid order_type. Must be 'full_report' or 'query'")
        
        # Validate user_query for query type
        if request.order_type == "query" and not request.user_query:
            raise HTTPException(status_code=400, detail="user_query is required for query type orders")
        
        # Set price based on order type
        if request.order_type == "query":
            amount = AstroConfig.AppSettings.QUERY_PRICE
        else:
            amount = AstroConfig.AppSettings.ANALYSIS_PRICE
        
        # Store user_query in birth_details if it's a query order
        birth_details = request.birth_details.copy() if request.birth_details else {}
        if request.order_type == "query" and request.user_query:
            birth_details["user_query"] = request.user_query
        
        order = order_service.create_order(
            db=db,
            user_id=current_user["user_id"],
            amount=amount,
            birth_details=birth_details,
            order_type=request.order_type
        )
        return OrderResponse(
            id=order.id,
            user_id=order.user_id,
            status=order.status,
            type=order.type,
            amount=order.amount,
            birth_details=order.birth_details,
            analysis_data=order.analysis_data,
            error_reason=order.error_reason,
            created_at=order.created_at,
            updated_at=order.updated_at
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating order: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to create order")


@app.get("/api/v1/orders", response_model=List[OrderResponse])
async def get_my_orders(
    current_user: dict = Depends(get_current_user_dependency),
    db: Session = Depends(get_db),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0)
):
    """Get current user's orders"""
    try:
        orders = order_service.get_user_orders(
            db=db,
            user_id=current_user["user_id"],
            limit=limit,
            offset=offset
        )
        return [
            OrderResponse(
                id=order.id,
                user_id=order.user_id,
                status=order.status,
                type=order.type,
                amount=order.amount,
                birth_details=order.birth_details,
                analysis_data=order.analysis_data,
                error_reason=order.error_reason,
                created_at=order.created_at,
                updated_at=order.updated_at
            )
            for order in orders
        ]
    except Exception as e:
        logger.error(f"Error getting orders: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to get orders")


@app.get("/api/v1/orders/{order_id}", response_model=OrderResponse)
async def get_order(
    order_id: int,
    current_user: dict = Depends(get_current_user_dependency),
    db: Session = Depends(get_db)
):
    """Get order by ID"""
    try:
        order = order_service.get_order(db, order_id, current_user["user_id"])
        if not order:
            raise HTTPException(status_code=404, detail="Order not found")
        return OrderResponse(
            id=order.id,
            user_id=order.user_id,
            status=order.status,
            type=order.type,
            amount=order.amount,
            birth_details=order.birth_details,
            analysis_data=order.analysis_data,
            error_reason=order.error_reason,
            created_at=order.created_at,
            updated_at=order.updated_at
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting order: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to get order")


# ==================== Payment Endpoints ====================

@app.post("/api/v1/payments/create", response_model=PaymentCreateResponse)
async def create_payment(
    order_id: int,
    current_user: dict = Depends(get_current_user_dependency),
    db: Session = Depends(get_db)
):
    """Create Razorpay payment order"""
    try:
        # Get order and verify ownership
        order = order_service.get_order(db, order_id, current_user["user_id"])
        if not order:
            raise HTTPException(status_code=404, detail="Order not found")
        
        if order.status != "payment_pending":
            raise HTTPException(status_code=400, detail="Order is not in payment_pending status")
        
        # Create Razorpay order
        razorpay_order = payment_service.create_order(order.amount, order.id)
        
        # Create payment record
        payment = Payment(
            order_id=order.id,
            razorpay_order_id=razorpay_order["id"],
            amount=order.amount,
            status="pending"
        )
        db.add(payment)
        db.commit()
        db.refresh(payment)
        
        # Update order with payment_id
        order.payment_id = payment.id
        db.commit()
        
        return PaymentCreateResponse(
            order_id=order.id,
            razorpay_order_id=razorpay_order["id"],
            amount=order.amount,
            key_id=AstroConfig.PaymentConfig.RAZORPAY_KEY_ID
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating payment: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to create payment")


@app.post("/api/v1/payments/verify")
async def verify_payment(
    request: PaymentVerifyRequest,
    current_user: dict = Depends(get_current_user_dependency),
    db: Session = Depends(get_db)
):
    """Verify Razorpay payment"""
    try:
        # Verify signature
        is_valid = payment_service.verify_payment(
            request.razorpay_order_id,
            request.razorpay_payment_id,
            request.razorpay_signature
        )
        
        if not is_valid:
            raise HTTPException(status_code=400, detail="Invalid payment signature")
        
        # Get payment record
        stmt = select(Payment).where(Payment.razorpay_order_id == request.razorpay_order_id)
        result = db.execute(stmt)
        payment = result.scalar_one_or_none()
        
        if not payment:
            raise HTTPException(status_code=404, detail="Payment not found")
        
        # Verify order ownership
        order = order_service.get_order(db, payment.order_id, current_user["user_id"])
        if not order:
            raise HTTPException(status_code=403, detail="Access denied")
        
        # Update payment
        payment.razorpay_payment_id = request.razorpay_payment_id
        payment.status = "success"
        db.commit()
        
        # Update order status and trigger analysis
        order_service.process_order(db, order.id)
        db.commit()
        
        # Trigger analysis asynchronously
        asyncio.create_task(process_order_analysis(order.id))
        
        return {"status": "success", "message": "Payment verified and analysis started"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error verifying payment: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to verify payment")


@app.post("/api/v1/payments/webhook")
async def payment_webhook(request: dict, db: Session = Depends(get_db)):
    """Handle Razorpay webhook"""
    try:
        # Verify webhook signature
        payload = json.dumps(request, sort_keys=True)
        signature = request.get("razorpay_signature", "")
        
        # Note: In production, get signature from headers
        # For now, we'll verify the payment directly
        
        event = request.get("event")
        payload_data = request.get("payload", {}).get("payment", {}).get("entity", {})
        
        if event == "payment.captured":
            razorpay_payment_id = payload_data.get("id")
            razorpay_order_id = payload_data.get("order_id")
            
            # Get payment record
            stmt = select(Payment).where(Payment.razorpay_order_id == razorpay_order_id)
            result = db.execute(stmt)
            payment = result.scalar_one_or_none()
            
            if payment and payment.status == "pending":
                payment.razorpay_payment_id = razorpay_payment_id
                payment.status = "success"
                payment.payment_method = payload_data.get("method", "unknown")
                db.commit()
                
                # Update order and trigger analysis
                order = order_service.get_order(db, payment.order_id)
                if order:
                    order_service.process_order(db, order.id)
                    db.commit()
                    asyncio.create_task(process_order_analysis(order.id))
        
        return {"status": "ok"}
    except Exception as e:
        logger.error(f"Webhook error: {e}", exc_info=True)
        return {"status": "error", "message": str(e)}


# ==================== Admin Endpoints ====================

@app.get("/api/v1/admin/orders")
async def admin_get_orders(
    admin: dict = Depends(get_current_admin),
    db: Session = Depends(get_db),
    status: Optional[str] = Query(None),
    user_id: Optional[int] = Query(None),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0)
):
    """Get all orders (admin only)"""
    try:
        orders, total = order_service.get_all_orders(
            db=db,
            status=status,
            user_id=user_id,
            limit=limit,
            offset=offset
        )
        return {
            "orders": [
                {
                    "id": order.id,
                    "user_id": order.user_id,
                    "user_email": order.user.email if order.user else None,
                    "type": order.type,
                    "status": order.status,
                    "amount": order.amount,
                    "error_reason": order.error_reason,
                    "created_at": order.created_at,
                    "updated_at": order.updated_at
                }
                for order in orders
            ],
            "total": total,
            "limit": limit,
            "offset": offset
        }
    except Exception as e:
        logger.error(f"Error getting admin orders: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to get orders")


@app.get("/api/v1/admin/orders/{order_id}")
async def admin_get_order(
    order_id: int,
    admin: dict = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Get order details (admin only)"""
    try:
        order = order_service.get_order(db, order_id)
        if not order:
            raise HTTPException(status_code=404, detail="Order not found")
        
        return {
            "id": order.id,
            "user_id": order.user_id,
            "user": {
                "id": order.user.id,
                "email": order.user.email,
                "name": order.user.name
            } if order.user else None,
            "type": order.type,
            "status": order.status,
            "amount": order.amount,
            "birth_details": order.birth_details,
            "analysis_data": order.analysis_data,
            "error_reason": order.error_reason,
            "payment": {
                "id": order.payment.id,
                "razorpay_order_id": order.payment.razorpay_order_id,
                "razorpay_payment_id": order.payment.razorpay_payment_id,
                "status": order.payment.status,
                "payment_method": order.payment.payment_method,
                "razorpay_refund_id": order.payment.razorpay_refund_id,
                "refund_amount": order.payment.refund_amount,
                "refund_status": order.payment.refund_status
            } if order.payment else None,
            "created_at": order.created_at,
            "updated_at": order.updated_at
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting admin order: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to get order")


@app.post("/api/v1/admin/orders/{order_id}/retry-analysis")
async def admin_retry_analysis(
    order_id: int,
    admin: dict = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Re-trigger analysis for an order (admin only)"""
    try:
        order = order_service.get_order(db, order_id)
        if not order:
            raise HTTPException(status_code=404, detail="Order not found")
        
        # Check that payment is successful
        if not order.payment or order.payment.status != "success":
            raise HTTPException(
                status_code=400,
                detail="Cannot retry analysis: payment must be successful"
            )
        
        # Reset order for retry
        reset_order = order_service.reset_order_for_retry(db, order_id)
        if not reset_order:
            raise HTTPException(status_code=500, detail="Failed to reset order for retry")
        
        # Trigger analysis asynchronously
        asyncio.create_task(process_order_analysis(order_id))
        
        return {
            "message": "Analysis re-triggered successfully",
            "order_id": order_id,
            "status": "processing"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrying analysis: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to retry analysis")


@app.post("/api/v1/admin/orders/{order_id}/refund")
async def admin_process_refund(
    order_id: int,
    admin: dict = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Process refund for an order (admin only)"""
    try:
        order = order_service.get_order(db, order_id)
        if not order:
            raise HTTPException(status_code=404, detail="Order not found")
        
        # Check that payment exists and is successful
        if not order.payment:
            raise HTTPException(
                status_code=400,
                detail="Cannot process refund: order has no payment"
            )
        
        if order.payment.status != "success":
            raise HTTPException(
                status_code=400,
                detail="Cannot process refund: payment must be successful"
            )
        
        # Check if already refunded
        if order.payment.refund_status == "processed" or order.payment.razorpay_refund_id:
            raise HTTPException(
                status_code=400,
                detail="Refund already processed for this payment"
            )
        
        # Check that payment has razorpay_payment_id
        if not order.payment.razorpay_payment_id:
            raise HTTPException(
                status_code=400,
                detail="Cannot process refund: payment ID not found"
            )
        
        # Create refund via Razorpay
        try:
            refund_data = payment_service.create_refund(
                order.payment.razorpay_payment_id,
                order.payment.amount
            )
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
        
        # Update payment record with refund details
        order.payment.razorpay_refund_id = refund_data.get("id")
        order.payment.refund_amount = order.payment.amount
        order.payment.refund_status = "processed"
        
        # Update order status to refunded
        order.status = "refunded"
        
        db.commit()
        db.refresh(order.payment)
        
        logger.info(f"Refund processed for order {order_id}: {refund_data.get('id')}")
        
        return {
            "message": "Refund processed successfully",
            "order_id": order_id,
            "refund_id": refund_data.get("id"),
            "refund_amount": order.payment.amount,
            "status": "refunded"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing refund: {e}", exc_info=True)
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to process refund")


@app.get("/api/v1/admin/stats")
async def admin_stats(
    admin: dict = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Get admin dashboard statistics"""
    try:
        from sqlalchemy import func, case
        
        # Total orders
        total_orders_stmt = select(func.count(Order.id))
        total_result = db.execute(total_orders_stmt)
        total_orders = total_result.scalar() or 0
        
        # Orders by status
        status_stmt = select(
            Order.status,
            func.count(Order.id).label("count")
        ).group_by(Order.status)
        status_result = db.execute(status_stmt)
        orders_by_status = {row[0]: row[1] for row in status_result.all()}
        
        # Total revenue
        revenue_stmt = select(func.sum(Order.amount)).where(Order.status == "completed")
        revenue_result = db.execute(revenue_stmt)
        total_revenue = revenue_result.scalar() or 0.0
        
        return {
            "total_orders": total_orders,
            "orders_by_status": orders_by_status,
            "total_revenue": total_revenue
        }
    except Exception as e:
        logger.error(f"Error getting admin stats: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to get stats")


# ==================== Analysis Processing ====================

async def process_order_analysis(order_id: int):
    """Process order analysis after payment"""
    from database import SessionLocal
    from services.chat_service import chat_service
    from graph.query_workflow import create_query_graph
    
    db = SessionLocal()
    try:
        order = order_service.get_order(db, order_id)
        if not order or order.status != "processing":
            return
        
        if _graph is None:
            order_service.fail_order(db, order_id, "AI service not available")
            return
        
        # Build message from birth details
        birth_details = order.birth_details or {}
        # Normalize field names: convert camelCase to snake_case for LangGraph compatibility
        normalized_birth_details = {
            "name": birth_details.get("name", "User"),
            "date_of_birth": birth_details.get("dateOfBirth") or birth_details.get("date_of_birth", ""),
            "time_of_birth": birth_details.get("timeOfBirth") or birth_details.get("time_of_birth", ""),
            "place_of_birth": birth_details.get("placeOfBirth") or birth_details.get("place_of_birth", ""),
            "goals": birth_details.get("goals", []),
            "latitude": birth_details.get("latitude"),
            "longitude": birth_details.get("longitude")
        }
        
        name = normalized_birth_details["name"]
        date_of_birth = normalized_birth_details["date_of_birth"]
        time_of_birth = normalized_birth_details["time_of_birth"]
        place_of_birth = normalized_birth_details["place_of_birth"]
        goals = normalized_birth_details["goals"]
        
        # Choose workflow based on order type
        if order.type == "query":
            # Use simplified query workflow
            query_graph = create_query_graph()
            user_query = birth_details.get("user_query", "")
            
            if not user_query:
                order_service.fail_order(db, order_id, "User query not found")
                db.commit()
                return
            
            # Build message with query and birth details
            message = f"{user_query}\n\nMy birth details:\n- Name: {name}\n- Date of Birth: {date_of_birth}\n- Time of Birth: {time_of_birth}\n- Place of Birth: {place_of_birth}"
            
            initial_state: AstroGuruState = {
                "user_message": message,
                "messages": [],
                "birth_details": normalized_birth_details,
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
                "request_type": "analysis"  # Route to analysis workflow
            }
            
            result = await query_graph.ainvoke(initial_state)
            
            # Get the response from messages (last assistant message)
            messages = result.get("messages", [])
            response_text = ""
            if messages:
                # Find last assistant message
                for msg in reversed(messages):
                    if msg.get("role") == "assistant":
                        response_text = msg.get("content", "")
                        break
            
            if response_text:
                # Save initial query and response as chat messages
                # Message 1: user query, Message 2: assistant response
                chat_service.save_chat_message(db, order_id, "user", user_query, 1)
                chat_service.save_chat_message(db, order_id, "assistant", response_text, 2)
                
                # Extract chart and dasha data from result for future follow-up messages
                chart_data = result.get("chart_data")
                dasha_data = result.get("dasha_data")
                
                # Mark order as completed with chart and dasha data
                analysis_data = {
                    "query_response": response_text,
                    "messages_count": 2,
                    "chart_data": chart_data,  # Save for follow-up messages
                    "dasha_data": dasha_data   # Save for follow-up messages
                }
                order_service.complete_order(db, order_id, analysis_data)
                db.commit()
                logger.info(f"Query order {order_id} processed successfully with chart and dasha data saved")
            else:
                order_service.fail_order(db, order_id, "No response generated for query")
                db.commit()
        else:
            # Full report workflow (existing logic)
            message = f"Hi, I'd like to get my horoscope analyzed. My details:\n- Name: {name}\n- Date of Birth: {date_of_birth}\n- Time of Birth: {time_of_birth}\n- Place of Birth: {place_of_birth}"
            
            if goals:
                message += f"\n- Goals: {', '.join(goals)}"
            
            initial_state: AstroGuruState = {
                "user_message": message,
                "messages": [],
                "birth_details": normalized_birth_details,
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
                "request_type": None
            }
            
            result = await _graph.ainvoke(initial_state)
            
            if result.get("analysis_complete"):
                # Extract analysis data
                analysis_data = {
                    "summary": result.get("summary"),
                    "chart_data_analysis": result.get("chart_data_analysis"),
                    "dasha_analysis": result.get("dasha_data", {}).get("analysis") if result.get("dasha_data") else None,
                    "goal_analysis": result.get("goal_analysis_data", {}).get("analysis") if result.get("goal_analysis_data") else None,
                    "recommendations": result.get("recommendation_data", {}).get("recommendations") if result.get("recommendation_data") else None
                }
                
                # Update order with analysis data
                order_service.complete_order(db, order_id, analysis_data)
                db.commit()
                
                # Get user for email
                stmt = select(User).where(User.id == order.user_id)
                user_result = db.execute(stmt)
                user = user_result.scalar_one_or_none()
                
                # Send email
                user_email = user.email if user else None
                if user_email:
                    success, error_msg = await send_analysis_email(
                        email=user_email,
                        name=name,
                        summary=analysis_data.get("summary", ""),
                        chart_analysis=analysis_data.get("chart_data_analysis"),
                        dasha_analysis=analysis_data.get("dasha_analysis"),
                        goal_analysis=analysis_data.get("goal_analysis"),
                        recommendations=analysis_data.get("recommendations")
                    )
                    
                    if not success:
                        # Mark order as failed due to email error
                        order_service.fail_order(db, order_id, f"Email not sent: {error_msg}")
                        db.commit()
            else:
                order_service.fail_order(db, order_id, "Analysis did not complete")
                db.commit()
            
    except Exception as e:
        logger.error(f"Error processing order analysis: {e}", exc_info=True)
        try:
            order_service.fail_order(db, order_id, f"Analysis error: {str(e)}")
            db.commit()
        except:
            db.rollback()
    finally:
        db.close()


# ==================== Chat Endpoints ====================

class ChatMessageRequest(BaseModel):
    message: str


class ChatMessageResponse(BaseModel):
    message: str
    message_number: int
    messages_remaining: int
    can_continue: bool


@app.post("/api/v1/orders/{order_id}/chat", response_model=ChatMessageResponse)
async def send_chat_message(
    order_id: int,
    request: ChatMessageRequest,
    current_user: dict = Depends(get_current_user_dependency),
    db: Session = Depends(get_db)
):
    """Send a chat message for a query order"""
    from services.chat_service import chat_service
    from graph.query_workflow import create_query_graph
    
    try:
        # Get order and verify ownership
        order = order_service.get_order(db, order_id, current_user["user_id"])
        if not order:
            raise HTTPException(status_code=404, detail="Order not found")
        
        # Verify order type is query
        if order.type != "query":
            raise HTTPException(
                status_code=400,
                detail="Chat is only available for query type orders"
            )
        
        # Verify payment is successful
        if not order.payment or order.payment.status != "success":
            raise HTTPException(
                status_code=400,
                detail="Payment must be successful to use chat"
            )
        
        # Check message limit (max 3 user messages total)
        if not chat_service.can_send_message(db, order_id, max_user_messages=3):
            raise HTTPException(
                status_code=400,
                detail="Message limit reached. Please create a new query order to continue."
            )
        
        # Get current user message count
        user_message_count = chat_service.get_user_message_count(db, order_id)
        next_message_number = chat_service.get_next_message_number(db, order_id)
        
        # Get birth details
        birth_details = order.birth_details or {}
        normalized_birth_details = {
            "name": birth_details.get("name", "User"),
            "date_of_birth": birth_details.get("dateOfBirth") or birth_details.get("date_of_birth", ""),
            "time_of_birth": birth_details.get("timeOfBirth") or birth_details.get("time_of_birth", ""),
            "place_of_birth": birth_details.get("placeOfBirth") or birth_details.get("place_of_birth", ""),
            "goals": birth_details.get("goals", []),
            "latitude": birth_details.get("latitude"),
            "longitude": birth_details.get("longitude")
        }
        
        # Get chat history for context (includes initial query and all follow-ups)
        chat_history = chat_service.get_chat_history(db, order_id)
        messages = []
        for msg in chat_history:
            messages.append({
                "role": msg.role,
                "content": msg.content
            })
        
        # Log conversation history for debugging
        logger.info(f"Order {order_id}: Passing {len(messages)} messages from conversation history to LangGraph")
        
        # Build user message
        user_message = request.message
        
        # Create query graph
        query_graph = create_query_graph()
        
        # Get chart and dasha data from order's analysis_data for follow-up messages
        chart_data = None
        dasha_data = None
        if order.analysis_data:
            chart_data = order.analysis_data.get("chart_data")
            dasha_data = order.analysis_data.get("dasha_data")
            logger.info(f"Order {order_id}: Retrieved chart_data and dasha_data from analysis_data for follow-up message")
        
        # Prepare state with chat history and chart/dasha data
        initial_state: AstroGuruState = {
            "user_message": user_message,
            "messages": messages,
            "birth_details": normalized_birth_details,
            "location_data": None,
            "chart_data": chart_data,  # Use saved chart data for context
            "dasha_data": dasha_data,  # Use saved dasha data for context
            "goal_analysis_data": None,
            "recommendation_data": None,
            "summary": None,
            "analysis_context": None,
            "current_step": None,
            "analysis_complete": True if chart_data and dasha_data else False,  # Mark complete if we have analysis data
            "error": None,
            "request_type": "analysis"  # Route to analysis workflow
        }
        
        # Process through query workflow
        result = await query_graph.ainvoke(initial_state)
        
        # Get the response from messages (last assistant message)
        updated_messages = result.get("messages", [])
        response_text = ""
        if updated_messages:
            # Find last assistant message
            for msg in reversed(updated_messages):
                if msg.get("role") == "assistant":
                    response_text = msg.get("content", "")
                    break
            
        if not response_text:
            raise HTTPException(status_code=500, detail="Failed to generate response")
        
        # Save user message and assistant response
        chat_service.save_chat_message(db, order_id, "user", user_message, next_message_number)
        chat_service.save_chat_message(db, order_id, "assistant", response_text, next_message_number + 1)
        
        # Check if user can continue (based on user message count)
        new_user_count = chat_service.get_user_message_count(db, order_id)
        can_continue = new_user_count < 3
        messages_remaining = max(0, 3 - new_user_count)
        
        return ChatMessageResponse(
            message=response_text,
            message_number=next_message_number + 1,
            messages_remaining=messages_remaining,
            can_continue=can_continue
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing chat message: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to process chat message")


@app.get("/api/v1/orders/{order_id}/chat/history")
async def get_chat_history(
    order_id: int,
    current_user: dict = Depends(get_current_user_dependency),
    db: Session = Depends(get_db)
):
    """Get chat history for an order"""
    from services.chat_service import chat_service
    
    try:
        # Get order and verify ownership
        order = order_service.get_order(db, order_id, current_user["user_id"])
        if not order:
            raise HTTPException(status_code=404, detail="Order not found")
        
        # Verify order type is query
        if order.type != "query":
            raise HTTPException(
                status_code=400,
                detail="Chat history is only available for query type orders"
            )
        
        # Get chat messages
        messages = chat_service.get_chat_history(db, order_id)
        
        # Get user message count
        user_message_count = chat_service.get_user_message_count(db, order_id)
        messages_remaining = max(0, 3 - user_message_count)
        
        return {
            "order_id": order_id,
            "messages": [
                {
                    "id": msg.id,
                    "message_number": msg.message_number,
                    "role": msg.role,
                    "content": msg.content,
                    "created_at": msg.created_at
                }
                for msg in messages
            ],
            "message_count": len(messages),
            "user_message_count": user_message_count,
            "messages_remaining": messages_remaining,
            "can_continue": user_message_count < 3
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting chat history: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to get chat history")


# ==================== Legacy Chat Endpoint (for backward compatibility) ====================

@app.post("/api/v1/chat", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    current_user: Optional[dict] = Depends(get_optional_user)
):
    """Chat endpoint - requires authentication and paid order"""
    if not current_user:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    if _graph is None:
        raise HTTPException(status_code=503, detail="AI service not available")
    
    # This endpoint is kept for backward compatibility
    # New flow should use orders -> payment -> analysis
    raise HTTPException(
        status_code=400,
        detail="Please use the order flow: create order -> pay -> analysis"
    )


# Catch-all route for React Router (must be last, after all API routes)
# This serves the React app for all non-API routes
@app.get("/{full_path:path}")
async def serve_react_app(full_path: str):
    """
    Serve React app for all non-API routes.
    This allows React Router to handle client-side routing.
    """
    # Don't serve React for API routes or static files
    if full_path.startswith("api/") or full_path.startswith("static/") or full_path.startswith("docs") or full_path.startswith("openapi.json"):
        raise HTTPException(status_code=404, detail="Not found")
    
    # Try React build first
    if react_build_exists:
        react_index = os.path.join(react_build_dir, "index.html")
        if os.path.exists(react_index):
            return FileResponse(react_index)
    
    # Fallback to legacy static files
    static_file = os.path.join(static_dir, "index.html")
    if os.path.exists(static_file):
        return FileResponse(static_file)
    
    raise HTTPException(status_code=404, detail="Not found")


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", AstroConfig.AppSettings.PORT))
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        reload=AstroConfig.AppSettings.DEBUG
    )
