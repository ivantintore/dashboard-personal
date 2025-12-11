# 🔐 Security Documentation - Dashboard Personal

## Overview

This document describes the security measures implemented in the Dashboard Personal platform.

## Authentication

### Google OAuth2
- All authentication is handled via Google OAuth2
- No passwords are stored in the system
- Users must be pre-authorized before they can log in

### Two-Factor Authentication (2FA)
- Optional TOTP-based 2FA using any authenticator app
- Backup codes provided for account recovery
- Each backup code can only be used once

### Session Management
- Secure, HTTP-only cookies
- 24-hour session duration (configurable)
- Sessions stored in encrypted database
- Sessions invalidated on role change

## Security Headers

All responses include:
- `Strict-Transport-Security` (HSTS)
- `X-Content-Type-Options: nosniff`
- `X-Frame-Options: DENY`
- `X-XSS-Protection: 1; mode=block`
- `Content-Security-Policy`
- `Permissions-Policy`
- `Referrer-Policy`

## Rate Limiting

Protection against brute force attacks:
- Login: 5 requests/minute per IP
- OAuth: 10 requests/minute per IP
- Admin actions: 20 requests/minute per IP
- API: 100 requests/minute per IP

## Audit Logging

All security events are logged:
- Login success/failure
- Logout
- User management (add/delete/role change)
- 2FA enable/disable
- Rate limit exceeded
- Suspicious activity

Logs are viewable at `/auth/admin/audit` (admin only).

## Secrets Management

### Environment Variables
All secrets are stored in environment variables:
- `AUTH_SECRET_KEY` - Session encryption key
- `GOOGLE_CLIENT_ID` / `GOOGLE_CLIENT_SECRET` - OAuth credentials
- `POSTGRES_PASSWORD` - Database password
- `REDIS_PASSWORD` - Cache password

### Secret Rotation
Run `./scripts/rotate-secrets.sh` to rotate secrets:
- Generates new secure random values
- Updates `.env` file
- Invalidates all existing sessions
- Creates backup of old `.env`

Recommended: Rotate secrets quarterly.

## Pre-Deployment Checklist

Run `./scripts/security-check.sh` before deploying:

```bash
./scripts/security-check.sh
```

This verifies:
- [ ] All required environment variables are set
- [ ] No default/insecure secrets
- [ ] No sensitive files in repository
- [ ] `.gitignore` properly configured

## Manual Security Checklist

### Before First Deploy
- [ ] Generate strong `AUTH_SECRET_KEY`: `openssl rand -hex 64`
- [ ] Generate strong `POSTGRES_PASSWORD`: `openssl rand -base64 32`
- [ ] Set up Google OAuth credentials in Google Cloud Console
- [ ] Set `ADMIN_EMAIL` to your email
- [ ] Remove any `client_secret*.json` files from repo

### After Deploy
- [ ] Verify HTTPS is working
- [ ] Test login flow
- [ ] Enable 2FA for admin accounts
- [ ] Review audit logs

### Regular Maintenance
- [ ] Rotate secrets quarterly
- [ ] Review audit logs weekly
- [ ] Update dependencies monthly
- [ ] Backup database weekly

## Security Contacts

If you discover a security vulnerability:
1. Do NOT create a public issue
2. Contact: [your-security-email]

## Incident Response

### If Secrets Are Compromised

1. Immediately rotate all secrets:
   ```bash
   ./scripts/rotate-secrets.sh
   ```

2. Restart all services:
   ```bash
   docker-compose -f docker-compose.full.yml down
   docker-compose -f docker-compose.full.yml up -d --build
   ```

3. Review audit logs for unauthorized access

4. Regenerate Google OAuth credentials if exposed

### If VPS Is Compromised

1. Change VPS password immediately
2. Rotate all application secrets
3. Review and revoke any suspicious sessions
4. Check for unauthorized changes to files
5. Consider rebuilding the server from scratch

## Security Architecture

```
┌─────────────┐     HTTPS      ┌─────────────┐
│   Client    │───────────────▶│    Caddy    │
└─────────────┘                │  (Gateway)  │
                               └──────┬──────┘
                                      │
                    ┌─────────────────┼─────────────────┐
                    │                 │                 │
                    ▼                 ▼                 ▼
             ┌────────────┐   ┌────────────┐   ┌────────────┐
             │   Auth     │   │  Dashboard │   │   Apps     │
             │  Service   │   │    Web     │   │            │
             └────────────┘   └────────────┘   └────────────┘
                    │
                    ▼
             ┌────────────┐
             │  SQLite    │
             │  (Auth DB) │
             └────────────┘
```

### Request Flow

1. Client makes request to `keonycs.com`
2. Caddy terminates TLS
3. Caddy adds security headers
4. For protected routes, Caddy calls `/auth/verify`
5. Auth service validates session cookie
6. If valid, request continues to backend service
7. If invalid, redirect to login

## Dependencies

Security-critical packages:
- `authlib` - OAuth2 implementation
- `python-jose` - JWT handling
- `slowapi` - Rate limiting
- `pyotp` - TOTP implementation

Keep these updated for security patches.
