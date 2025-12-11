"""
Auth Service - Google OAuth2 Authentication
Dashboard Personal - Ivan Tintore
"""
import os
import secrets
from datetime import datetime, timedelta
from typing import Optional

from fastapi import FastAPI, Request, Response, HTTPException, Form, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware
from authlib.integrations.starlette_client import OAuth
from jose import jwt

import database

# Configuration
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID", "")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET", "")
SECRET_KEY = os.getenv("SECRET_KEY", secrets.token_hex(32))
SESSION_DURATION_HOURS = int(os.getenv("SESSION_DURATION_HOURS", "24"))
BASE_URL = os.getenv("BASE_URL", "https://keonycs.com")
COOKIE_NAME = "auth_session"
COOKIE_DOMAIN = os.getenv("COOKIE_DOMAIN", "keonycs.com")

# Initialize FastAPI
app = FastAPI(title="Auth Service", docs_url=None, redoc_url=None)
app.add_middleware(SessionMiddleware, secret_key=SECRET_KEY)

# Templates
templates = Jinja2Templates(directory="templates")

# OAuth setup
oauth = OAuth()
oauth.register(
    name='google',
    client_id=GOOGLE_CLIENT_ID,
    client_secret=GOOGLE_CLIENT_SECRET,
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_kwargs={'scope': 'openid email profile'}
)


@app.on_event("startup")
async def startup():
    """Initialize database on startup"""
    database.init_db()
    database.cleanup_expired_sessions()
    print("✅ Auth Service initialized")
    if not GOOGLE_CLIENT_ID or not GOOGLE_CLIENT_SECRET:
        print("⚠️  WARNING: Google OAuth credentials not configured!")


def get_current_user(request: Request) -> Optional[dict]:
    """Get current user from session cookie"""
    session_id = request.cookies.get(COOKIE_NAME)
    if not session_id:
        return None
    session = database.get_session(session_id)
    return session


def require_auth(request: Request) -> dict:
    """Dependency that requires authentication"""
    user = get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    return user


def require_admin(request: Request) -> dict:
    """Dependency that requires admin role"""
    user = require_auth(request)
    if user.get('role') != 'admin':
        raise HTTPException(status_code=403, detail="Admin access required")
    return user


# ==================== AUTH ENDPOINTS ====================

@app.get("/auth/login", response_class=HTMLResponse)
async def login_page(request: Request, next: str = "/tools/"):
    """Login page with Google button"""
    user = get_current_user(request)
    if user:
        return RedirectResponse(url=next, status_code=302)
    
    return templates.TemplateResponse("login.html", {
        "request": request,
        "next": next
    })


@app.get("/auth/google")
async def google_login(request: Request, next: str = "/tools/"):
    """Redirect to Google OAuth"""
    request.session['next_url'] = next
    redirect_uri = f"{BASE_URL}/auth/callback"
    return await oauth.google.authorize_redirect(request, redirect_uri)


@app.get("/auth/callback")
async def google_callback(request: Request):
    """Handle Google OAuth callback"""
    try:
        token = await oauth.google.authorize_access_token(request)
    except Exception as e:
        print(f"OAuth error: {e}")
        return RedirectResponse(url="/auth/login?error=oauth_failed", status_code=302)
    
    user_info = token.get('userinfo')
    if not user_info:
        return RedirectResponse(url="/auth/login?error=no_userinfo", status_code=302)
    
    email = user_info.get('email')
    name = user_info.get('name')
    picture = user_info.get('picture')
    
    # Check if user is authorized
    db_user = database.get_user_by_email(email)
    if not db_user:
        return templates.TemplateResponse("denied.html", {
            "request": request,
            "email": email
        }, status_code=403)
    
    # Update user info and create session
    db_user = database.create_or_update_user(email, name, picture)
    session_id = secrets.token_urlsafe(32)
    expires_at = datetime.now() + timedelta(hours=SESSION_DURATION_HOURS)
    database.create_session(db_user['id'], session_id, expires_at)
    
    # Redirect to original destination
    next_url = request.session.pop('next_url', '/tools/')
    response = RedirectResponse(url=next_url, status_code=302)
    response.set_cookie(
        key=COOKIE_NAME,
        value=session_id,
        httponly=True,
        secure=True,
        samesite='lax',
        max_age=SESSION_DURATION_HOURS * 3600,
        domain=COOKIE_DOMAIN if COOKIE_DOMAIN != "localhost" else None
    )
    return response


@app.get("/auth/logout")
async def logout(request: Request):
    """Logout and clear session"""
    session_id = request.cookies.get(COOKIE_NAME)
    if session_id:
        database.delete_session(session_id)
    
    response = RedirectResponse(url="/auth/login", status_code=302)
    response.delete_cookie(key=COOKIE_NAME, domain=COOKIE_DOMAIN if COOKIE_DOMAIN != "localhost" else None)
    return response


@app.get("/auth/verify")
async def verify_session(request: Request):
    """Verify session for Caddy forward_auth"""
    user = get_current_user(request)
    if user:
        return Response(
            status_code=200,
            headers={
                "X-Auth-User": user.get('email', ''),
                "X-Auth-Name": user.get('name', ''),
                "X-Auth-Role": user.get('role', 'user')
            }
        )
    return Response(status_code=401)


# ==================== ADMIN PANEL ====================

@app.get("/auth/admin", response_class=HTMLResponse)
async def admin_panel(request: Request, user: dict = Depends(require_admin)):
    """Admin panel to manage users"""
    users = database.get_all_users()
    return templates.TemplateResponse("admin.html", {
        "request": request,
        "user": user,
        "users": users,
        "success": request.query_params.get('success'),
        "error": request.query_params.get('error')
    })


@app.post("/auth/admin/add-user")
async def add_user(
    request: Request,
    email: str = Form(...),
    role: str = Form("user"),
    user: dict = Depends(require_admin)
):
    """Add a new authorized user"""
    if not email or '@' not in email:
        return RedirectResponse(url="/auth/admin?error=invalid_email", status_code=302)
    
    success = database.add_user(email.lower().strip(), role)
    if success:
        return RedirectResponse(url="/auth/admin?success=user_added", status_code=302)
    return RedirectResponse(url="/auth/admin?error=user_exists", status_code=302)


@app.post("/auth/admin/delete-user/{user_id}")
async def delete_user(
    request: Request,
    user_id: int,
    user: dict = Depends(require_admin)
):
    """Delete a user"""
    if user_id == user.get('user_id'):
        return RedirectResponse(url="/auth/admin?error=cannot_delete_self", status_code=302)
    
    success = database.delete_user(user_id)
    if success:
        return RedirectResponse(url="/auth/admin?success=user_deleted", status_code=302)
    return RedirectResponse(url="/auth/admin?error=cannot_delete", status_code=302)


@app.post("/auth/admin/update-role/{user_id}")
async def update_role(
    request: Request,
    user_id: int,
    role: str = Form(...),
    user: dict = Depends(require_admin)
):
    """Update user role"""
    database.update_user_role(user_id, role)
    return RedirectResponse(url="/auth/admin?success=role_updated", status_code=302)


# ==================== HEALTH CHECK ====================

@app.get("/auth/health")
async def health():
    """Health check endpoint"""
    return {"status": "healthy", "service": "auth-service"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)

