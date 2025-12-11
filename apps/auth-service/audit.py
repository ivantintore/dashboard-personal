"""
Audit Logging and Security Alerts for Auth Service
Tracks security events and sends alerts for critical issues
"""
import os
import json
import httpx
from datetime import datetime
from typing import Optional, Dict, Any
from enum import Enum

# Configuration
ALERT_WEBHOOK_URL = os.getenv("ALERT_WEBHOOK_URL", "")
ALERT_THRESHOLD_FAILED_LOGINS = 5
ALERT_THRESHOLD_RATE_LIMIT = 10

class EventType(str, Enum):
    """Security event types"""
    LOGIN_SUCCESS = "LOGIN_SUCCESS"
    LOGIN_FAILED = "LOGIN_FAILED"
    LOGOUT = "LOGOUT"
    SESSION_CREATED = "SESSION_CREATED"
    SESSION_EXPIRED = "SESSION_EXPIRED"
    SESSION_INVALIDATED = "SESSION_INVALIDATED"
    
    USER_ADDED = "USER_ADDED"
    USER_DELETED = "USER_DELETED"
    ROLE_CHANGED = "ROLE_CHANGED"
    
    TOTP_ENABLED = "2FA_ENABLED"
    TOTP_DISABLED = "2FA_DISABLED"
    TOTP_VERIFIED = "2FA_VERIFIED"
    TOTP_FAILED = "2FA_FAILED"
    BACKUP_CODE_USED = "BACKUP_CODE_USED"
    
    RATE_LIMIT_EXCEEDED = "RATE_LIMIT_EXCEEDED"
    SUSPICIOUS_ACTIVITY = "SUSPICIOUS_ACTIVITY"
    UNAUTHORIZED_ACCESS = "UNAUTHORIZED_ACCESS"
    
    ADMIN_ACTION = "ADMIN_ACTION"
    CONFIG_CHANGED = "CONFIG_CHANGED"

class Severity(str, Enum):
    """Event severity levels"""
    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"

# Severity mapping for event types
EVENT_SEVERITY = {
    EventType.LOGIN_SUCCESS: Severity.INFO,
    EventType.LOGIN_FAILED: Severity.WARNING,
    EventType.LOGOUT: Severity.INFO,
    EventType.SESSION_CREATED: Severity.DEBUG,
    EventType.SESSION_EXPIRED: Severity.DEBUG,
    EventType.SESSION_INVALIDATED: Severity.INFO,
    
    EventType.USER_ADDED: Severity.INFO,
    EventType.USER_DELETED: Severity.WARNING,
    EventType.ROLE_CHANGED: Severity.WARNING,
    
    EventType.TOTP_ENABLED: Severity.INFO,
    EventType.TOTP_DISABLED: Severity.WARNING,
    EventType.TOTP_VERIFIED: Severity.DEBUG,
    EventType.TOTP_FAILED: Severity.WARNING,
    EventType.BACKUP_CODE_USED: Severity.WARNING,
    
    EventType.RATE_LIMIT_EXCEEDED: Severity.WARNING,
    EventType.SUSPICIOUS_ACTIVITY: Severity.ERROR,
    EventType.UNAUTHORIZED_ACCESS: Severity.ERROR,
    
    EventType.ADMIN_ACTION: Severity.INFO,
    EventType.CONFIG_CHANGED: Severity.WARNING,
}

# Events that should trigger alerts
ALERT_EVENTS = {
    EventType.SUSPICIOUS_ACTIVITY,
    EventType.UNAUTHORIZED_ACCESS,
    EventType.USER_DELETED,
    EventType.ROLE_CHANGED,
    EventType.TOTP_DISABLED,
}


class AuditLogger:
    """Audit logger with database persistence and alerting"""
    
    def __init__(self, db_module):
        self.db = db_module
        self._failed_login_counts: Dict[str, int] = {}
        self._rate_limit_counts: Dict[str, int] = {}
    
    def log(
        self,
        event_type: EventType,
        user_id: Optional[int] = None,
        email: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        severity: Optional[Severity] = None
    ):
        """Log a security event"""
        if severity is None:
            severity = EVENT_SEVERITY.get(event_type, Severity.INFO)
        
        # Prepare details JSON
        details_json = json.dumps(details) if details else None
        
        # Store in database
        try:
            self.db.create_audit_log(
                event_type=event_type.value,
                user_id=user_id,
                email=email,
                ip_address=ip_address,
                user_agent=user_agent[:500] if user_agent else None,
                details=details_json,
                severity=severity.value
            )
        except Exception as e:
            print(f"Failed to write audit log: {e}")
        
        # Check for alert conditions
        self._check_alerts(event_type, email, ip_address, details)
        
        # Print to console for debugging
        print(f"[AUDIT] {datetime.now().isoformat()} | {severity.value.upper()} | {event_type.value} | {email or 'anonymous'} | {ip_address}")
    
    def _check_alerts(
        self,
        event_type: EventType,
        email: Optional[str],
        ip_address: Optional[str],
        details: Optional[Dict]
    ):
        """Check if event should trigger an alert"""
        should_alert = False
        alert_message = ""
        
        # Direct alert events
        if event_type in ALERT_EVENTS:
            should_alert = True
            alert_message = f"Security Event: {event_type.value}"
            if email:
                alert_message += f" | User: {email}"
            if ip_address:
                alert_message += f" | IP: {ip_address}"
        
        # Failed login threshold
        if event_type == EventType.LOGIN_FAILED and ip_address:
            self._failed_login_counts[ip_address] = self._failed_login_counts.get(ip_address, 0) + 1
            if self._failed_login_counts[ip_address] >= ALERT_THRESHOLD_FAILED_LOGINS:
                should_alert = True
                alert_message = f"Multiple failed logins ({self._failed_login_counts[ip_address]}) from IP: {ip_address}"
                # Reset counter after alert
                self._failed_login_counts[ip_address] = 0
        
        # Rate limit threshold
        if event_type == EventType.RATE_LIMIT_EXCEEDED and ip_address:
            self._rate_limit_counts[ip_address] = self._rate_limit_counts.get(ip_address, 0) + 1
            if self._rate_limit_counts[ip_address] >= ALERT_THRESHOLD_RATE_LIMIT:
                should_alert = True
                alert_message = f"Repeated rate limiting ({self._rate_limit_counts[ip_address]}) from IP: {ip_address}"
                self._rate_limit_counts[ip_address] = 0
        
        if should_alert:
            self._send_alert(alert_message, event_type, details)
    
    def _send_alert(
        self,
        message: str,
        event_type: EventType,
        details: Optional[Dict] = None
    ):
        """Send alert via webhook"""
        if not ALERT_WEBHOOK_URL:
            print(f"[ALERT] {message}")
            return
        
        try:
            severity = EVENT_SEVERITY.get(event_type, Severity.WARNING)
            
            # Format for Slack/Discord compatible webhook
            payload = {
                "text": f"🚨 **Security Alert** - {message}",
                "attachments": [{
                    "color": self._severity_color(severity),
                    "fields": [
                        {"title": "Event", "value": event_type.value, "short": True},
                        {"title": "Severity", "value": severity.value.upper(), "short": True},
                        {"title": "Time", "value": datetime.now().isoformat(), "short": True},
                    ]
                }]
            }
            
            if details:
                payload["attachments"][0]["fields"].append({
                    "title": "Details",
                    "value": json.dumps(details, indent=2)[:1000],
                    "short": False
                })
            
            # Send async in background (fire and forget)
            with httpx.Client(timeout=5.0) as client:
                client.post(ALERT_WEBHOOK_URL, json=payload)
        
        except Exception as e:
            print(f"Failed to send alert: {e}")
    
    def _severity_color(self, severity: Severity) -> str:
        """Get color for severity level"""
        colors = {
            Severity.DEBUG: "#808080",
            Severity.INFO: "#2196F3",
            Severity.WARNING: "#FF9800",
            Severity.ERROR: "#F44336",
            Severity.CRITICAL: "#9C27B0",
        }
        return colors.get(severity, "#808080")
    
    def get_recent_events(
        self,
        limit: int = 100,
        event_type: Optional[EventType] = None,
        user_id: Optional[int] = None,
        severity: Optional[Severity] = None
    ):
        """Get recent audit events"""
        return self.db.get_audit_logs(
            limit=limit,
            event_type=event_type.value if event_type else None,
            user_id=user_id,
            severity=severity.value if severity else None
        )
    
    def get_failed_login_count(self, ip_address: str, minutes: int = 60) -> int:
        """Get failed login count for IP in last N minutes"""
        return self.db.count_events_by_ip(
            ip_address=ip_address,
            event_type=EventType.LOGIN_FAILED.value,
            minutes=minutes
        )
