# AstroGuru AI - Vedic Astrology Analysis Platform

An AI-powered astrology analysis system using **LangGraph** and **Gemini Models** to provide comprehensive horoscope analysis with authentication, payment integration, and admin management.

## Features

### Core Astrology Features
1. **Intelligent Routing**: Automatically determines if user wants analysis or general chat
2. **Chart Generation**: Generates Lagna and Divisional charts in South Indian style
3. **Dasha Analysis**: Generates lifetime and on-demand Dasha/Bhukthi reports
4. **Goal-Oriented Analysis**: Detailed analysis for specific goals (career, marriage, love life, etc.)
5. **Recommendations**: Provides detailed recommendations and remedies based on analysis
6. **Location Resolution**: Automatically resolves place names to geographic coordinates
7. **Email Reports**: Automatic email delivery of complete astrology reports

### Platform Features
1. **Google OAuth Authentication**: Secure user login with Google
2. **Payment Integration**: Razorpay payment gateway for UPI, cards, and netbanking
3. **Order Management**: Complete order lifecycle tracking
4. **User Dashboard**: View order history and past analysis reports
5. **Admin Panel**: Comprehensive admin dashboard with order management, filters, and statistics
6. **Error Handling**: Robust error handling with order status tracking

## Prerequisites

1. **Python 3.11 or higher**
2. **PostgreSQL Database** (12 or higher)
3. **Google AI API Key** (for Gemini models)
4. **Google OAuth Credentials** (for authentication)
5. **Razorpay Account** (for payments)
6. **Resend API Key** (for email delivery)

## Installation

### Step 1: Clone/Navigate to the Project

```bash
cd /path/to/astroguru-ai-langgraph-repo/astroguru-ai
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
# Upgrade build tools first
pip install --upgrade pip setuptools wheel

# Install dependencies
pip install -r requirements.txt
```

**Note**: The application uses `psycopg2-binary` for PostgreSQL connectivity, which is a pre-compiled binary package that doesn't require build tools.

### Step 4: Set Up PostgreSQL Database

1. **Install PostgreSQL** (if not already installed):
   ```bash
   # macOS
   brew install postgresql
   brew services start postgresql
   
   # Ubuntu/Debian
   sudo apt-get install postgresql postgresql-contrib
   ```

2. **Create Database**:
   
   **For macOS (Homebrew installation):**
   ```bash
   # Connect to PostgreSQL (uses your system username as default)
   psql postgres
   # OR if that doesn't work:
   psql -d postgres
   
   # Create database
   CREATE DATABASE astroguru_db;
   
   # Exit
   \q
   ```
   
   **For Linux/Windows (standard installation):**
   ```bash
   # Connect to PostgreSQL
   psql -U postgres
   
   # Create database
   CREATE DATABASE astroguru_db;
   
   # Exit
   \q
   ```
   
   **Note**: On macOS with Homebrew, PostgreSQL uses your system username (e.g., `yml`) as the default superuser instead of `postgres`. If you get "role postgres does not exist", use `psql postgres` or `psql -d postgres` instead.

3. **Run Migrations**:
   ```bash
   # Make sure you're in the project directory
   cd /path/to/astroguru-ai
   
   # Run migrations (creates all tables)
   alembic upgrade head
   ```
   
   **Note**: Alembic requires `psycopg2-binary` for synchronous database connections. It's included in `requirements.txt` and will be installed automatically. If you get async connection errors, ensure `psycopg2-binary` is installed:
   ```bash
   pip install psycopg2-binary
   ```

### Step 5: Configure Environment Variables

Create a `.env` file in the project root:

```bash
touch .env
```

Add the following configuration (see `.env.example` for template):

```env
# Database Configuration
# For macOS Homebrew: Use your system username (e.g., yml) instead of postgres
# For Linux/Windows: Use postgres as shown below
DATABASE_URL=postgresql://yml@localhost:5432/astroguru_db
# OR for standard installation:
# DATABASE_URL=postgresql://postgres:postgres@localhost:5432/astroguru_db

# Google OAuth Configuration
GOOGLE_CLIENT_ID=your_google_client_id_here
GOOGLE_CLIENT_SECRET=your_google_client_secret_here
GOOGLE_REDIRECT_URI=http://localhost:8002/api/v1/auth/google/callback

# Razorpay Configuration
RAZORPAY_KEY_ID=your_razorpay_key_id_here
RAZORPAY_KEY_SECRET=your_razorpay_key_secret_here
RAZORPAY_WEBHOOK_SECRET=your_razorpay_webhook_secret_here

# JWT Configuration
JWT_SECRET_KEY=your_secret_key_change_in_production_min_32_chars
JWT_ALGORITHM=HS256
JWT_EXPIRATION_HOURS=24

# Admin Configuration
ADMIN_EMAIL=admin@astroguru.ai
ADMIN_PASSWORD=your_secure_password_hash_here

# Application Settings
PORT=8002
DEBUG=false
ENV=dev

# Analysis Price (in INR)
ANALYSIS_PRICE=10.00

# Google AI (Gemini) Configuration
GEMINI_API_KEY=your_gemini_api_key_here
GEMINI_MODEL=gemini-2.5-flash
GEMINI_TEMPERATURE=0.2
GEMINI_MAX_TOKENS=8192

# Email Configuration (Resend)
RESEND_API_KEY=your_resend_api_key_here
RESEND_FROM_EMAIL=astroguruai@resend.dev
RESEND_FROM_NAME=AstroGuru AI

# Frontend URL (for OAuth redirects)
FRONTEND_URL=http://localhost:8002
```

### Step 6: Set Up Google OAuth

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing one
3. Enable **Google+ API** (or **Google Identity Services API**)
4. Go to **Credentials** → **Create Credentials** → **OAuth 2.0 Client ID**
5. Configure OAuth consent screen
6. **Add Authorized JavaScript origins**:
   - **Development**: `http://localhost:8002`
   - **Production**: `https://your-domain.com` (add this when deploying)
   
   **Note**: These are the domains from which your JavaScript can initiate OAuth requests. Include the protocol (http/https) but no trailing slash or path.

7. **Add Authorized redirect URIs**:
   - **Development**: `http://localhost:8002/api/v1/auth/google/callback`
   - **Production**: `https://your-domain.com/api/v1/auth/google/callback` (add this when deploying)
   
   **Note**: These are the exact URLs where Google will redirect users after authentication.

8. Copy **Client ID** and **Client Secret** to `.env` file

**Configuration Summary:**
- **Authorized JavaScript origins**: The domain where your frontend is hosted
  - Dev: `http://localhost:8002`
  - Prod: `https://your-domain.com`
  
- **Authorized redirect URIs**: The callback endpoint on your backend
  - Dev: `http://localhost:8002/api/v1/auth/google/callback`
  - Prod: `https://your-domain.com/api/v1/auth/google/callback`

**Note for Production:**
- You can use the **same Google Cloud project** for both development and production
- Simply add **multiple authorized JavaScript origins and redirect URIs** in the OAuth client configuration
- Alternatively, create **separate OAuth credentials** (same project, different Client IDs) for dev and prod environments
- Update `GOOGLE_REDIRECT_URI` in production `.env` to your production domain with HTTPS
- Example production redirect URI: `https://astroguru.ai/api/v1/auth/google/callback`

### Step 7: Set Up Razorpay

1. Sign up at [Razorpay](https://razorpay.com/)
2. Go to **Settings** → **API Keys**
3. Generate **Key ID** and **Key Secret** (use test keys for development)
4. Set up webhook (optional but recommended):
   - Go to **Settings** → **Webhooks**
   - Add webhook URL: `https://your-domain.com/api/v1/payments/webhook`
   - Select events: `payment.captured`
   - Copy webhook secret to `.env`

### Step 8: Set Up Resend (Email)

1. Sign up at [Resend](https://resend.com/)
2. Get API key from [API Keys](https://resend.com/api-keys)
3. Verify domain (or use `onboarding@resend.dev` for testing)
4. Add API key to `.env`

## Running the Application

### Start the FastAPI Server

```bash
# Make sure virtual environment is activated
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Start the server
uvicorn main:app --reload --host 0.0.0.0 --port 8002
```

The `--reload` flag enables auto-reload on code changes (useful for development).

**Access the Application:**
- **Web Interface**: http://localhost:8002/
- **API Documentation (Swagger UI)**: http://localhost:8002/docs
- **Alternative API Docs (ReDoc)**: http://localhost:8002/redoc
- **Admin Panel**: http://localhost:8002/static/admin.html
- **Health Check**: http://localhost:8002/health

## User Journey

### 1. User Registration/Login

1. User visits the website
2. Clicks "Login with Google"
3. Redirected to Google OAuth
4. After authentication, redirected back with JWT token
5. User is logged in and sees welcome page

### 2. Order Creation & Payment

1. User clicks "Start Your Analysis" from welcome page
2. Fills in birth details form:
   - Full Name
   - Date of Birth
   - Time of Birth (IST)
   - Place of Birth (with autocomplete)
   - Goals (career, marriage, health, etc.)
3. Clicks "Pay and Generate"
4. Order is created with status `payment_pending`
5. Razorpay payment page opens
6. User completes payment (UPI/Card/Netbanking)
7. Payment is verified
8. Order status changes to `processing`
9. User sees success page: "Payment successful, report will be emailed once generated"

### 3. Analysis Processing

1. After payment verification, AI analysis is triggered automatically
2. System processes:
   - Location resolution
   - Chart generation
   - Dasha calculation
   - Goal analysis
   - Recommendations
   - Summary generation
3. Analysis results are stored in order
4. Email is sent to user (if email service available)
5. Order status changes to `completed` or `failed` (if email fails)

### 4. Viewing Reports

1. User can access dashboard to view all orders
2. Completed orders show "View Report" button
3. User can view full analysis report with:
   - Summary
   - Chart Analysis
   - Dasha Analysis
   - Goal Analysis
   - Recommendations

## API Endpoints

### Authentication Endpoints

#### Initiate Google OAuth
**Endpoint**: `GET /api/v1/auth/google`

**Description**: Get Google OAuth URL for authentication

**Response**:
```json
{
  "auth_url": "https://accounts.google.com/o/oauth2/v2/auth?..."
}
```

#### Google OAuth Callback
**Endpoint**: `GET /api/v1/auth/google/callback?code={code}`

**Description**: Handle OAuth callback and create/update user

**Response**: Redirects to frontend with token

#### Admin Login
**Endpoint**: `POST /api/v1/auth/admin/login`

**Request Body**:
```json
{
  "email": "admin@astroguru.ai",
  "password": "password"
}
```

**Response**:
```json
{
  "access_token": "jwt_token_here",
  "token_type": "bearer",
  "user_type": "admin"
}
```

#### Get Current User
**Endpoint**: `GET /api/v1/auth/me`

**Headers**: `Authorization: Bearer {token}`

**Response**:
```json
{
  "id": 1,
  "email": "user@example.com",
  "name": "User Name",
  "picture_url": "https://...",
  "type": "user"
}
```

### Order Endpoints

#### Create Order
**Endpoint**: `POST /api/v1/orders`

**Headers**: `Authorization: Bearer {token}`

**Request Body**:
```json
{
  "birth_details": {
    "name": "John Doe",
    "dateOfBirth": "1990-05-15",
    "timeOfBirth": "14:30",
    "placeOfBirth": "Mumbai, Maharashtra, India",
    "latitude": "19.0760",
    "longitude": "72.8777",
    "goals": ["career", "marriage"]
  }
}
```

**Response**:
```json
{
  "id": 1,
  "user_id": 1,
  "status": "payment_pending",
  "amount": 10.00,
  "birth_details": {...},
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z"
}
```

#### Get User Orders
**Endpoint**: `GET /api/v1/orders?limit=50&offset=0`

**Headers**: `Authorization: Bearer {token}`

**Response**:
```json
[
  {
    "id": 1,
    "user_id": 1,
    "status": "completed",
    "amount": 10.00,
    "birth_details": {...},
    "analysis_data": {...},
    "created_at": "2024-01-01T00:00:00Z"
  }
]
```

#### Get Order by ID
**Endpoint**: `GET /api/v1/orders/{order_id}`

**Headers**: `Authorization: Bearer {token}`

**Response**: Same as order object above

### Payment Endpoints

#### Create Payment
**Endpoint**: `POST /api/v1/payments/create?order_id={order_id}`

**Headers**: `Authorization: Bearer {token}`

**Response**:
```json
{
  "order_id": 1,
  "razorpay_order_id": "order_xxx",
  "amount": 10.00,
  "key_id": "rzp_test_xxx",
  "currency": "INR"
}
```

#### Verify Payment
**Endpoint**: `POST /api/v1/payments/verify`

**Headers**: `Authorization: Bearer {token}`

**Request Body**:
```json
{
  "razorpay_order_id": "order_xxx",
  "razorpay_payment_id": "pay_xxx",
  "razorpay_signature": "signature_xxx"
}
```

**Response**:
```json
{
  "status": "success",
  "message": "Payment verified and analysis started"
}
```

#### Payment Webhook
**Endpoint**: `POST /api/v1/payments/webhook`

**Description**: Handle Razorpay webhook events (payment.captured)

**Note**: Webhook signature verification is recommended in production

### Admin Endpoints

#### Get All Orders (Admin)
**Endpoint**: `GET /api/v1/admin/orders?status={status}&user_id={user_id}&limit=50&offset=0`

**Headers**: `Authorization: Bearer {admin_token}`

**Response**:
```json
{
  "orders": [
    {
      "id": 1,
      "user_id": 1,
      "user_email": "user@example.com",
      "status": "completed",
      "amount": 10.00,
      "error_reason": null,
      "created_at": "2024-01-01T00:00:00Z",
      "updated_at": "2024-01-01T00:00:00Z"
    }
  ],
  "total": 100,
  "limit": 50,
  "offset": 0
}
```

#### Get Order Details (Admin)
**Endpoint**: `GET /api/v1/admin/orders/{order_id}`

**Headers**: `Authorization: Bearer {admin_token}`

**Response**: Complete order details with user, payment, and analysis data

#### Get Admin Statistics
**Endpoint**: `GET /api/v1/admin/stats`

**Headers**: `Authorization: Bearer {admin_token}`

**Response**:
```json
{
  "total_orders": 100,
  "orders_by_status": {
    "payment_pending": 5,
    "processing": 10,
    "completed": 80,
    "failed": 5
  },
  "total_revenue": 1000.00
}
```

## Admin Panel

### Accessing Admin Panel

**For React App (Recommended)**:
1. Navigate to `http://localhost:3000/admin` (React dev server)
   - Or `http://localhost:8002/admin` if using production build

**For Legacy Static Files**:
1. Navigate to `http://localhost:8002/static/admin.html`

**Login**:
2. Enter admin credentials from your `.env` file:
   - **Email**: Value of `ADMIN_EMAIL` (default: `admin@astroguru.ai`)
   - **Password**: The original password (not the hash - system hashes it for comparison)
   
3. **Note**: If you need to generate a password hash, see `ADMIN_ACCESS.md` for instructions.

**Access dashboard with**:
   - Order statistics
   - Order listing with filters
   - Order details view
   - Pagination support

### Admin Features

- **Statistics Dashboard**: Total orders, revenue, status breakdown
- **Order Management**: View all orders with pagination
- **Filters**: Filter by status, user ID
- **Order Details**: View complete order information including:
  - User details
  - Payment information
  - Birth details
  - Analysis data
  - Error reasons (if failed)

## Database Schema

### Users Table
- `id`: Primary key
- `email`: Unique email address
- `name`: User's full name
- `google_id`: Google OAuth ID
- `picture_url`: Profile picture URL
- `created_at`, `updated_at`: Timestamps

### Orders Table
- `id`: Primary key
- `user_id`: Foreign key to users
- `status`: payment_pending | processing | completed | failed
- `payment_id`: Foreign key to payments
- `amount`: Order amount
- `birth_details`: JSON field with birth information
- `analysis_data`: JSON field with analysis results
- `error_reason`: Text field for error messages
- `created_at`, `updated_at`: Timestamps

### Payments Table
- `id`: Primary key
- `order_id`: Foreign key to orders
- `razorpay_order_id`: Razorpay order ID
- `razorpay_payment_id`: Razorpay payment ID
- `amount`: Payment amount
- `status`: pending | success | failed
- `payment_method`: UPI, card, netbanking, etc.
- `created_at`, `updated_at`: Timestamps

## Order Status Flow

```
payment_pending → (after payment) → processing → (after analysis) → completed
                                                      ↓
                                                   (if email fails)
                                                      ↓
                                                   failed
```

## Error Handling

### Email Failures
- If email sending fails, order status is set to `failed`
- Error reason is stored in `error_reason` field
- Admin can view failed orders and retry if needed

### Payment Failures
- Payment failures are logged
- User can retry payment from dashboard
- Order remains in `payment_pending` status

### Analysis Failures
- Analysis errors are caught and logged
- Order status set to `failed` with error reason
- Admin can investigate and retry

## Testing

### Test Authentication

```bash
# Get OAuth URL
curl http://localhost:8002/api/v1/auth/google

# Admin login
curl -X POST http://localhost:8002/api/v1/auth/admin/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@astroguru.ai",
    "password": "password"
  }'
```

### Test Order Creation

```bash
# Create order (requires auth token)
curl -X POST http://localhost:8002/api/v1/orders \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer {token}" \
  -d '{
    "birth_details": {
      "name": "Test User",
      "dateOfBirth": "1990-01-01",
      "timeOfBirth": "12:00",
      "placeOfBirth": "Mumbai, India",
      "goals": ["career"]
    }
  }'
```

### Test Payment

```bash
# Create payment
curl -X POST "http://localhost:8002/api/v1/payments/create?order_id=1" \
  -H "Authorization: Bearer {token}"

# Verify payment (after Razorpay callback)
curl -X POST http://localhost:8002/api/v1/payments/verify \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer {token}" \
  -d '{
    "razorpay_order_id": "order_xxx",
    "razorpay_payment_id": "pay_xxx",
    "razorpay_signature": "signature_xxx"
  }'
```

### Test Payment Webhook (Local Testing)

Since webhooks are called by external services, you can simulate Razorpay webhook calls locally:

```bash
# Replace {razorpay_order_id} with actual order ID from your database
# Replace {razorpay_payment_id} with a test payment ID (e.g., "pay_test123")

curl -X POST http://localhost:8002/api/v1/payments/webhook \
  -H "Content-Type: application/json" \
  -d '{
    "event": "payment.captured",
    "payload": {
      "payment": {
        "entity": {
          "id": "pay_test123",
          "order_id": "order_ABC123XYZ",
          "method": "upi",
          "amount": 1000,
          "currency": "INR",
          "status": "captured"
        }
      }
    },
    "razorpay_signature": "test_signature"
  }'
```

**Note**: 
- Replace `order_ABC123XYZ` with an actual `razorpay_order_id` from your `payments` table
- The webhook will update the payment status and trigger order processing
- For local testing, signature verification is skipped if `RAZORPAY_WEBHOOK_SECRET` is not set
- To get the actual `razorpay_order_id`, check your database:
  ```sql
  SELECT razorpay_order_id FROM payments WHERE order_id = 1;
  ```

## Troubleshooting

### Database Connection Issues

**Error**: `Database not initialized` or connection errors

**Solution**:
- Verify PostgreSQL is running: `pg_isready`
- Check `DATABASE_URL` in `.env` is correct
- Ensure database exists: `psql -U postgres -l` (Linux) or `psql -l` (macOS)
- Run migrations: `alembic upgrade head`

**Error**: `role "postgres" does not exist` (macOS)

**Solution**:
- On macOS with Homebrew, PostgreSQL uses your system username as the default superuser
- Connect using: `psql postgres` or `psql -d postgres` (without `-U postgres`)
- Update `DATABASE_URL` in `.env` to use your username instead of `postgres`:
  ```env
  DATABASE_URL=postgresql://yml@localhost:5432/astroguru_db
  ```
- If you need to create a `postgres` user:
  ```sql
  CREATE USER postgres WITH SUPERUSER PASSWORD 'postgres';
  ```

### OAuth Issues

**Error**: OAuth callback fails or redirects incorrectly

**Solution**:
- Verify `GOOGLE_REDIRECT_URI` matches Google Cloud Console settings
- Check `FRONTEND_URL` is set correctly
- Ensure OAuth consent screen is configured
- Check client ID and secret are correct

### Payment Issues

**Error**: Payment creation fails or verification fails

**Solution**:
- Verify Razorpay keys are correct (test keys for development)
- Check webhook secret is set (optional but recommended)
- Ensure payment amount is in paise (amount * 100)
- Check Razorpay dashboard for payment status

### Email Issues

**Error**: Emails not sending or order marked as failed

**Solution**:
- Verify `RESEND_API_KEY` is set
- Check domain is verified in Resend
- Check email service logs
- Failed orders can be retried by admin

## Deployment

### Production Checklist

1. **Environment Variables**:
   - Use production database URL
   - Set strong `JWT_SECRET_KEY`
   - Use production Razorpay keys
   - Set production `FRONTEND_URL` (e.g., `https://astroguru.ai`)
   - Update `GOOGLE_REDIRECT_URI` to production URL (e.g., `https://astroguru.ai/api/v1/auth/google/callback`)
   - Add production redirect URI in Google Cloud Console OAuth credentials
   - Hash admin password properly

2. **Database**:
   - Run migrations: `alembic upgrade head`
   - Set up database backups
   - Configure connection pooling

3. **Security**:
   - Enable HTTPS
   - Set secure CORS origins in `.env`:
     ```env
     CORS_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
     CORS_ALLOW_CREDENTIALS=true
     ```
     **Important**: Never use `CORS_ORIGINS=*` in production!
   - Use environment-based secrets
   - Enable webhook signature verification

4. **Monitoring**:
   - Set up error logging
   - Monitor order processing
   - Track payment success rates
   - Monitor email delivery

## Project Structure

```
astroguru-ai/
├── alembic/                   # Database migrations
│   ├── versions/
│   ├── env.py
│   └── script.py.mako
├── auth/                      # Authentication module
│   ├── __init__.py
│   ├── jwt_handler.py        # JWT token handling
│   ├── oauth.py              # Google OAuth
│   ├── admin_auth.py         # Admin authentication
│   └── dependencies.py       # FastAPI dependencies
├── models/                    # Database models
│   ├── __init__.py
│   ├── user.py
│   ├── order.py
│   └── payment.py
├── services/                  # Business logic services
│   ├── email_service.py
│   ├── payment_service.py    # Razorpay integration
│   └── order_service.py      # Order management
├── static/                    # Frontend files
│   ├── index.html
│   ├── admin.html
│   ├── app.js
│   ├── auth.js
│   ├── dashboard.js
│   ├── admin.js
│   └── style.css
├── graph/                     # LangGraph workflow
│   ├── nodes/
│   ├── state.py
│   └── workflow.py
├── config.py                  # Configuration
├── database.py                # Database connection
├── main.py                    # FastAPI application
├── requirements.txt
├── alembic.ini
└── .env.example
```

## License

Same as original astroguru-ai project.

## Support

For issues or questions:
1. Check the troubleshooting section
2. Review API documentation at `/docs`
3. Check server logs for detailed error messages
4. Verify all environment variables are set correctly
