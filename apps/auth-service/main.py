"""
Auth Service - Google OAuth2 Authentication with Enterprise Security
Dashboard Personal - Ivan Tintore

Security features:
- Google OAuth2 authentication
- Rate limiting on all endpoints
- CSRF protection
- Open redirect prevention
- Security headers
- 2FA/TOTP support
- Audit logging
"""
import os
import secrets
from datetime import datetime, timedelta
from typing import Optional

from fastapi import FastAPI, Request, Response, HTTPException, Form, Depends
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware
from authlib.integrations.starlette_client import OAuth
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

import database
from security import (
    limiter, validate_redirect_url, add_security_headers,
    validate_email, sanitize_string, validate_role,
    is_suspicious_request, get_real_ip, rate_limit_exceeded_handler,
    RATE_LIMITS
)
from audit import AuditLogger, EventType, Severity
import totp as totp_utils

# ==================== CONFIGURATION ====================

GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID", "")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET", "")
SECRET_KEY = os.getenv("SECRET_KEY", "")
SESSION_DURATION_HOURS = int(os.getenv("SESSION_DURATION_HOURS", "24"))
BASE_URL = os.getenv("BASE_URL", "https://keonycs.com")
COOKIE_NAME = "auth_session"
COOKIE_DOMAIN = os.getenv("COOKIE_DOMAIN", "keonycs.com")

# Validate required configuration
if not SECRET_KEY or SECRET_KEY == "supersecretkey123":
    raise ValueError("SECRET_KEY must be set to a secure random value!")

# ==================== INITIALIZE APP ====================

app = FastAPI(title="Auth Service", docs_url=None, redoc_url=None, openapi_url=None)

# Add rate limiter
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, rate_limit_exceeded_handler)

# Add session middleware
app.add_middleware(SessionMiddleware, secret_key=SECRET_KEY, max_age=3600)

# Add security headers middleware
@app.middleware("http")
async def security_headers_middleware(request: Request, call_next):
    return await add_security_headers(request, call_next)

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

# Audit logger
audit = AuditLogger(database)

# ==================== STARTUP ====================

@app.on_event("startup")
async def startup():
    """Initialize database on startup"""
    database.init_db()
    cleaned = database.cleanup_expired_sessions()
    if cleaned:
        print(f"🧹 Cleaned {cleaned} expired sessions")
    print("✅ Auth Service initialized with enterprise security")
    if not GOOGLE_CLIENT_ID or not GOOGLE_CLIENT_SECRET:
        print("⚠️  WARNING: Google OAuth credentials not configured!")


# ==================== AUTH HELPERS ====================

def get_current_user(request: Request) -> Optional[dict]:
    """Get current user from session cookie"""
    session_id = request.cookies.get(COOKIE_NAME)
    if not session_id:
        return None
    session = database.get_session(session_id)
    if not session:
        return None
    
    # Check if 2FA is required but not verified
    if session.get('totp_enabled') and not session.get('is_2fa_verified'):
        return None
    
    return session


def get_pending_2fa_user(request: Request) -> Optional[dict]:
    """Get user who has authenticated but not completed 2FA"""
    session_id = request.cookies.get(COOKIE_NAME)
    if not session_id:
        return None
    session = database.get_session(session_id)
    if not session:
        return None
    
    # Return session only if 2FA is pending
    if session.get('totp_enabled') and not session.get('is_2fa_verified'):
        return session
    
    return None


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
        audit.log(
            EventType.UNAUTHORIZED_ACCESS,
            user_id=user.get('user_id'),
            email=user.get('email'),
            ip_address=get_real_ip(request),
            details={"attempted_resource": "/auth/admin"}
        )
        raise HTTPException(status_code=403, detail="Admin access required")
    return user


# ==================== AUTH ENDPOINTS ====================

@app.get("/auth/login", response_class=HTMLResponse)
@limiter.limit(RATE_LIMITS["login"])
async def login_page(request: Request, next: str = "/tools/"):
    """Login page with Google button"""
    # Check for suspicious activity
    if is_suspicious_request(request):
        audit.log(
            EventType.SUSPICIOUS_ACTIVITY,
            ip_address=get_real_ip(request),
            user_agent=request.headers.get("User-Agent"),
            details={"endpoint": "/auth/login"}
        )
    
    user = get_current_user(request)
    if user:
        return RedirectResponse(url=validate_redirect_url(next), status_code=302)
    
    # Check if 2FA is pending
    pending_user = get_pending_2fa_user(request)
    if pending_user:
        return RedirectResponse(url="/auth/2fa", status_code=302)
    
    return templates.TemplateResponse("login.html", {
        "request": request,
        "next": validate_redirect_url(next)
    })


@app.get("/auth/google")
@limiter.limit(RATE_LIMITS["google_auth"])
async def google_login(request: Request, next: str = "/tools/"):
    """Redirect to Google OAuth"""
    request.session['next_url'] = validate_redirect_url(next)
    redirect_uri = f"{BASE_URL}/auth/callback"
    return await oauth.google.authorize_redirect(request, redirect_uri)


@app.get("/auth/callback")
@limiter.limit(RATE_LIMITS["callback"])
async def google_callback(request: Request):
    """Handle Google OAuth callback"""
    ip_address = get_real_ip(request)
    user_agent = request.headers.get("User-Agent", "")
    
    try:
        token = await oauth.google.authorize_access_token(request)
    except Exception as e:
        print(f"OAuth error: {e}")
        audit.log(
            EventType.LOGIN_FAILED,
            ip_address=ip_address,
            user_agent=user_agent,
            details={"error": "oauth_failed", "message": str(e)}
        )
        return RedirectResponse(url="/auth/login?error=oauth_failed", status_code=302)
    
    user_info = token.get('userinfo')
    if not user_info:
        audit.log(
            EventType.LOGIN_FAILED,
            ip_address=ip_address,
            user_agent=user_agent,
            details={"error": "no_userinfo"}
        )
        return RedirectResponse(url="/auth/login?error=no_userinfo", status_code=302)
    
    email = user_info.get('email')
    name = user_info.get('name')
    picture = user_info.get('picture')
    
    # Check if user is authorized
    db_user = database.get_user_by_email(email)
    if not db_user:
        audit.log(
            EventType.LOGIN_FAILED,
            email=email,
            ip_address=ip_address,
            user_agent=user_agent,
            details={"error": "user_not_authorized"}
        )
        return templates.TemplateResponse("denied.html", {
            "request": request,
            "email": email
        }, status_code=403)
    
    # Update user info and create session
    db_user = database.create_or_update_user(email, name, picture)
    session_id = secrets.token_urlsafe(32)
    expires_at = datetime.now() + timedelta(hours=SESSION_DURATION_HOURS)
    
    # Check if 2FA is enabled
    is_2fa_verified = not db_user.get('totp_enabled', False)
    
    database.create_session(
        user_id=db_user['id'],
        session_id=session_id,
        expires_at=expires_at,
        ip_address=ip_address,
        user_agent=user_agent,
        is_2fa_verified=is_2fa_verified
    )
    
    audit.log(
        EventType.LOGIN_SUCCESS,
        user_id=db_user['id'],
        email=email,
        ip_address=ip_address,
        user_agent=user_agent,
        details={"2fa_required": not is_2fa_verified}
    )
    
    # Redirect based on 2FA status
    if db_user.get('totp_enabled'):
        next_url = "/auth/2fa"
    else:
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
    user = get_current_user(request) or get_pending_2fa_user(request)
    
    if session_id:
        database.delete_session(session_id)
        if user:
            audit.log(
                EventType.LOGOUT,
                user_id=user.get('user_id'),
                email=user.get('email'),
                ip_address=get_real_ip(request)
            )
    
    response = RedirectResponse(url="/auth/login", status_code=302)
    response.delete_cookie(key=COOKIE_NAME, domain=COOKIE_DOMAIN if COOKIE_DOMAIN != "localhost" else None)
    return response


@app.get("/auth/verify")
async def verify_session(request: Request, next: str = "/tools/"):
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
    
    # Not authenticated - redirect to login
    # Caddy forward_auth will follow this redirect
    redirect_url = f"/auth/login?next={validate_redirect_url(next)}"
    return RedirectResponse(url=redirect_url, status_code=302)


# ==================== 2FA ENDPOINTS ====================

@app.get("/auth/2fa", response_class=HTMLResponse)
@limiter.limit(RATE_LIMITS["login"])
async def totp_page(request: Request):
    """2FA verification page"""
    user = get_pending_2fa_user(request)
    if not user:
        return RedirectResponse(url="/auth/login", status_code=302)
    
    return templates.TemplateResponse("2fa.html", {
        "request": request,
        "email": user.get('email')
    })


@app.post("/auth/2fa/verify")
@limiter.limit(RATE_LIMITS["login"])
async def verify_totp(request: Request, code: str = Form(...)):
    """Verify TOTP code"""
    ip_address = get_real_ip(request)
    user = get_pending_2fa_user(request)
    
    if not user:
        return RedirectResponse(url="/auth/login", status_code=302)
    
    session_id = request.cookies.get(COOKIE_NAME)
    totp_info = database.get_totp_info(user['user_id'])
    
    # Try TOTP code first
    if totp_utils.verify_totp(totp_info['totp_secret'], code):
        database.update_session_2fa_verified(session_id)
        audit.log(
            EventType.TOTP_VERIFIED,
            user_id=user.get('user_id'),
            email=user.get('email'),
            ip_address=ip_address
        )
        next_url = request.session.pop('next_url', '/tools/')
        return RedirectResponse(url=next_url, status_code=302)
    
    # Try backup code
    is_valid, remaining_codes = totp_utils.verify_backup_code(totp_info['backup_codes'], code)
    if is_valid:
        database.update_backup_codes(user['user_id'], remaining_codes)
        database.update_session_2fa_verified(session_id)
        audit.log(
            EventType.BACKUP_CODE_USED,
            user_id=user.get('user_id'),
            email=user.get('email'),
            ip_address=ip_address,
            details={"remaining_codes": totp_utils.get_backup_codes_count(remaining_codes)}
        )
        next_url = request.session.pop('next_url', '/tools/')
        return RedirectResponse(url=next_url, status_code=302)
    
    # Invalid code
    audit.log(
        EventType.TOTP_FAILED,
        user_id=user.get('user_id'),
        email=user.get('email'),
        ip_address=ip_address
    )
    
    return templates.TemplateResponse("2fa.html", {
        "request": request,
        "email": user.get('email'),
        "error": "invalid_code"
    })


@app.get("/auth/2fa/setup", response_class=HTMLResponse)
@limiter.limit(RATE_LIMITS["admin"])
async def setup_2fa_page(request: Request, user: dict = Depends(require_auth)):
    """2FA setup page"""
    totp_info = database.get_totp_info(user['user_id'])
    
    if totp_info and totp_info.get('totp_enabled'):
        return RedirectResponse(url="/auth/2fa/manage", status_code=302)
    
    # Generate new secret if not exists
    secret = totp_info.get('totp_secret') if totp_info else None
    if not secret:
        secret = totp_utils.generate_totp_secret()
        database.set_totp_secret(user['user_id'], secret)
    
    qr_code = totp_utils.generate_qr_code(secret, user['email'])
    manual_key = totp_utils.format_secret_for_manual_entry(secret)
    
    return templates.TemplateResponse("2fa_setup.html", {
        "request": request,
        "user": user,
        "qr_code": qr_code,
        "manual_key": manual_key
    })


@app.post("/auth/2fa/setup")
@limiter.limit(RATE_LIMITS["admin"])
async def enable_2fa(request: Request, code: str = Form(...), user: dict = Depends(require_auth)):
    """Enable 2FA after verifying first code"""
    totp_info = database.get_totp_info(user['user_id'])
    
    if not totp_info or not totp_info.get('totp_secret'):
        return RedirectResponse(url="/auth/2fa/setup", status_code=302)
    
    if totp_utils.verify_totp(totp_info['totp_secret'], code):
        # Generate backup codes
        backup_codes, stored_codes = totp_utils.generate_backup_codes()
        database.enable_totp(user['user_id'], stored_codes)
        
        audit.log(
            EventType.TOTP_ENABLED,
            user_id=user.get('user_id'),
            email=user.get('email'),
            ip_address=get_real_ip(request)
        )
        
        return templates.TemplateResponse("2fa_backup_codes.html", {
            "request": request,
            "user": user,
            "backup_codes": backup_codes
        })
    
    # Invalid code - show setup again
    secret = totp_info['totp_secret']
    qr_code = totp_utils.generate_qr_code(secret, user['email'])
    manual_key = totp_utils.format_secret_for_manual_entry(secret)
    
    return templates.TemplateResponse("2fa_setup.html", {
        "request": request,
        "user": user,
        "qr_code": qr_code,
        "manual_key": manual_key,
        "error": "invalid_code"
    })


@app.get("/auth/2fa/manage", response_class=HTMLResponse)
@limiter.limit(RATE_LIMITS["admin"])
async def manage_2fa_page(request: Request, user: dict = Depends(require_auth)):
    """2FA management page"""
    totp_info = database.get_totp_info(user['user_id'])
    
    return templates.TemplateResponse("2fa_manage.html", {
        "request": request,
        "user": user,
        "totp_enabled": totp_info.get('totp_enabled') if totp_info else False,
        "backup_codes_count": totp_utils.get_backup_codes_count(totp_info.get('backup_codes', '')) if totp_info else 0
    })


@app.post("/auth/2fa/disable")
@limiter.limit(RATE_LIMITS["admin"])
async def disable_2fa(request: Request, code: str = Form(...), user: dict = Depends(require_auth)):
    """Disable 2FA"""
    totp_info = database.get_totp_info(user['user_id'])
    
    if not totp_info or not totp_info.get('totp_enabled'):
        return RedirectResponse(url="/auth/2fa/manage", status_code=302)
    
    # Verify code before disabling
    if totp_utils.verify_totp(totp_info['totp_secret'], code):
        database.disable_totp(user['user_id'])
        
        audit.log(
            EventType.TOTP_DISABLED,
            user_id=user.get('user_id'),
            email=user.get('email'),
            ip_address=get_real_ip(request)
        )
        
        return RedirectResponse(url="/auth/2fa/manage?success=disabled", status_code=302)
    
    return RedirectResponse(url="/auth/2fa/manage?error=invalid_code", status_code=302)


# ==================== ADMIN PANEL ====================

@app.get("/auth/admin", response_class=HTMLResponse)
@limiter.limit(RATE_LIMITS["admin"])
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
@limiter.limit(RATE_LIMITS["admin"])
async def add_user(
    request: Request,
    email: str = Form(...),
    role: str = Form("user"),
    user: dict = Depends(require_admin)
):
    """Add a new authorized user"""
    email = sanitize_string(email.lower())
    role = validate_role(role)
    
    if not validate_email(email):
        return RedirectResponse(url="/auth/admin?error=invalid_email", status_code=302)
    
    success = database.add_user(email, role)
    if success:
        audit.log(
            EventType.USER_ADDED,
            user_id=user.get('user_id'),
            email=user.get('email'),
            ip_address=get_real_ip(request),
            details={"added_email": email, "role": role}
        )
        return RedirectResponse(url="/auth/admin?success=user_added", status_code=302)
    return RedirectResponse(url="/auth/admin?error=user_exists", status_code=302)


@app.post("/auth/admin/delete-user/{user_id}")
@limiter.limit(RATE_LIMITS["admin"])
async def delete_user(
    request: Request,
    user_id: int,
    user: dict = Depends(require_admin)
):
    """Delete a user"""
    if user_id == user.get('user_id'):
        return RedirectResponse(url="/auth/admin?error=cannot_delete_self", status_code=302)
    
    target_user = database.get_user_by_id(user_id)
    success = database.delete_user(user_id)
    
    if success:
        audit.log(
            EventType.USER_DELETED,
            user_id=user.get('user_id'),
            email=user.get('email'),
            ip_address=get_real_ip(request),
            details={"deleted_email": target_user.get('email') if target_user else None}
        )
        return RedirectResponse(url="/auth/admin?success=user_deleted", status_code=302)
    return RedirectResponse(url="/auth/admin?error=cannot_delete", status_code=302)


@app.post("/auth/admin/update-role/{user_id}")
@limiter.limit(RATE_LIMITS["admin"])
async def update_role(
    request: Request,
    user_id: int,
    role: str = Form(...),
    user: dict = Depends(require_admin)
):
    """Update user role"""
    role = validate_role(role)
    target_user = database.get_user_by_id(user_id)
    old_role = target_user.get('role') if target_user else None
    
    database.update_user_role(user_id, role)
    
    # Invalidate user sessions if role changed
    if old_role != role:
        database.delete_user_sessions(user_id)
        audit.log(
            EventType.ROLE_CHANGED,
            user_id=user.get('user_id'),
            email=user.get('email'),
            ip_address=get_real_ip(request),
            details={
                "target_email": target_user.get('email') if target_user else None,
                "old_role": old_role,
                "new_role": role
            }
        )
    
    return RedirectResponse(url="/auth/admin?success=role_updated", status_code=302)


@app.get("/auth/admin/audit", response_class=HTMLResponse)
@limiter.limit(RATE_LIMITS["admin"])
async def audit_logs_page(request: Request, user: dict = Depends(require_admin)):
    """View audit logs"""
    logs = database.get_audit_logs(limit=200)
    return templates.TemplateResponse("audit.html", {
        "request": request,
        "user": user,
        "logs": logs
    })


# ==================== HEALTH CHECK ====================

@app.get("/auth/health")
async def health():
    """Health check endpoint"""
    return {"status": "healthy", "service": "auth-service", "security": "enterprise"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
