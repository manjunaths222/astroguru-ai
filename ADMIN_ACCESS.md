# Admin Portal Access Guide

## Quick Access

**URL**: `http://localhost:3000/admin` (React app) or `http://localhost:8002/admin` (legacy)

## Login Credentials

The admin credentials are configured in your `.env` file:

```env
ADMIN_EMAIL=admin@astroguru.ai
ADMIN_PASSWORD=your_password_hash_here
```

## Setting Up Admin Password

If you need to generate a password hash:

1. **Using Python**:
   ```python
   from auth.admin_auth import get_password_hash
   password_hash = get_password_hash("your_secure_password")
   print(password_hash)
   ```

2. **Add to .env**:
   ```env
   ADMIN_PASSWORD=<generated_hash>
   ```

3. **Restart backend** for changes to take effect

## Login Steps

1. Navigate to `/admin` in your browser
   - React app: `http://localhost:3000/admin`
   - Legacy: `http://localhost:8002/admin`
   
2. Enter your admin email (from `ADMIN_EMAIL` in `.env`)
   - Default: `admin@astroguru.ai`

3. Enter your password
   - **Important**: Enter the **original plain text password** (not the hash)
   - The system automatically hashes it and compares with the hash in `.env`
   - If your `.env` has a plain text password, enter that exact password
   - If your `.env` has a hashed password (starts with `$2b$`), enter the original password that was hashed

4. Click "Login"

## Admin Features

Once logged in, you can:

- **View All Orders**: See all orders from all users with pagination
- **View Order Details**: Click "View" to see complete order information
- **Re-trigger Analysis**: Restart analysis for failed or completed full report orders
- **Process Refunds**: Issue full refunds for completed orders via Razorpay
- **Filter Orders**: Filter by status, user ID, etc.

## Troubleshooting

### "Login failed" error
- Verify `ADMIN_EMAIL` and `ADMIN_PASSWORD` in `.env` are correct
- Make sure you're using the original password (not the hash) when logging in
- Check that the password hash was generated correctly

### Can't access `/admin` route
- Make sure you're using the correct URL (React: port 3000, Legacy: port 8002)
- Verify the route exists in `App.tsx` (React) or `main.py` (legacy)
- Check browser console for errors

### Admin link not showing in navbar
- The admin link only appears if you're logged in as an admin
- After admin login, refresh the page to see the admin link in the navbar

