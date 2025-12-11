"""
Security utilities for Auth Service
Rate limiting, CSRF, headers, and validation
"""
import os
import re
from urllib.parse import urlparse
from typing import Optional
from functools import wraps

from fastapi import Request, Response, HTTPException
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

# ==================== CONFIGURATION ====================

# Allowed hosts for redirects (prevent open redirect attacks)
ALLOWED_REDIRECT_HOSTS = {
    "keonycs.com",
    "www.keonycs.com",
    "localhost",
    "127.0.0.1"
}

# Rate limit configuration
RATE_LIMITS = {
    "login": "5/minute",
    "google_auth": "10/minute",
    "callback": "10/minute",
    "admin": "20/minute",
    "api": "100/minute"
}

# ==================== RATE LIMITER ====================

def get_real_ip(request: Request) -> str:
    """Get real client IP, considering proxies"""
    # Check X-Forwarded-For header (set by Caddy)
    forwarded_for = request.headers.get("X-Forwarded-For")
    if forwarded_for:
        # Get the first IP in the chain (original client)
        return forwarded_for.split(",")[0].strip()
    
    # Check X-Real-IP header
    real_ip = request.headers.get("X-Real-IP")
    if real_ip:
        return real_ip
    
    # Fallback to direct client IP
    return get_remote_address(request)

limiter = Limiter(key_func=get_real_ip)

# ==================== REDIRECT VALIDATION ====================

def validate_redirect_url(url: str, default: str = "/tools/") -> str:
    """
    Validate and sanitize redirect URL to prevent open redirect attacks.
    Only allows:
    - Relative paths starting with /
    - Absolute URLs to allowed hosts
    """
    if not url:
        return default
    
    # Clean the URL
    url = url.strip()
    
    # Allow relative paths
    if url.startswith("/"):
        # Prevent protocol-relative URLs (//evil.com)
        if url.startswith("//"):
            return default
        # Prevent backslash tricks
        if "\\" in url:
            return default
        return url
    
    # Check absolute URLs
    try:
        parsed = urlparse(url)
        if parsed.scheme not in ("http", "https"):
            return default
        if parsed.netloc and parsed.netloc.lower() not in ALLOWED_REDIRECT_HOSTS:
            return default
        return url
    except Exception:
        return default

# ==================== SECURITY HEADERS ====================

SECURITY_HEADERS = {
    "X-Content-Type-Options": "nosniff",
    "X-Frame-Options": "DENY",
    "X-XSS-Protection": "1; mode=block",
    "Referrer-Policy": "strict-origin-when-cross-origin",
    "Permissions-Policy": "geolocation=(), microphone=(), camera=()",
    "Cache-Control": "no-store, no-cache, must-revalidate, private",
    "Pragma": "no-cache"
}

async def add_security_headers(request: Request, call_next):
    """Middleware to add security headers to all responses"""
    response = await call_next(request)
    
    for header, value in SECURITY_HEADERS.items():
        response.headers[header] = value
    
    return response

# ==================== INPUT VALIDATION ====================

EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')

def validate_email(email: str) -> bool:
    """Validate email format"""
    if not email or len(email) > 254:
        return False
    return bool(EMAIL_REGEX.match(email))

def sanitize_string(value: str, max_length: int = 255) -> str:
    """Sanitize string input"""
    if not value:
        return ""
    # Remove null bytes and control characters
    value = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', value)
    # Truncate to max length
    return value[:max_length].strip()

# ==================== ROLE VALIDATION ====================

VALID_ROLES = {"user", "admin"}

def validate_role(role: str) -> str:
    """Validate and normalize role"""
    role = role.lower().strip() if role else "user"
    return role if role in VALID_ROLES else "user"

# ==================== SUSPICIOUS ACTIVITY DETECTION ====================

def is_suspicious_request(request: Request) -> bool:
    """Detect potentially suspicious requests"""
    user_agent = request.headers.get("User-Agent", "")
    
    # No user agent
    if not user_agent:
        return True
    
    # Known scanner/bot patterns
    suspicious_patterns = [
        "sqlmap", "nikto", "nmap", "masscan",
        "burp", "owasp", "dirbuster", "gobuster",
        "hydra", "medusa", "nessus", "acunetix"
    ]
    
    ua_lower = user_agent.lower()
    for pattern in suspicious_patterns:
        if pattern in ua_lower:
            return True
    
    return False

# ==================== RATE LIMIT EXCEEDED HANDLER ====================

def rate_limit_exceeded_handler(request: Request, exc: RateLimitExceeded):
    """Custom handler for rate limit exceeded"""
    return Response(
        content="Rate limit exceeded. Please try again later.",
        status_code=429,
        headers={
            "Retry-After": "60",
            "X-RateLimit-Limit": str(exc.detail)
        }
    )
