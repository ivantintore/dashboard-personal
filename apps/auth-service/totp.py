"""
Two-Factor Authentication (2FA/TOTP) for Auth Service
Uses pyotp for TOTP generation and verification
"""
import os
import secrets
import base64
from io import BytesIO
from typing import Optional, List, Tuple

import pyotp
import qrcode
from qrcode.image.pil import PilImage

# Configuration
TOTP_ISSUER = os.getenv("TOTP_ISSUER", "Dashboard-MAITSA")
BACKUP_CODES_COUNT = 10
BACKUP_CODE_LENGTH = 8

# ==================== TOTP FUNCTIONS ====================

def generate_totp_secret() -> str:
    """Generate a new TOTP secret for a user"""
    return pyotp.random_base32()


def get_totp_uri(secret: str, email: str) -> str:
    """Generate the TOTP provisioning URI for QR code"""
    totp = pyotp.TOTP(secret)
    return totp.provisioning_uri(name=email, issuer_name=TOTP_ISSUER)


def generate_qr_code(secret: str, email: str) -> str:
    """
    Generate QR code for TOTP setup.
    Returns base64-encoded PNG image.
    """
    uri = get_totp_uri(secret, email)
    
    # Generate QR code
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(uri)
    qr.make(fit=True)
    
    # Create image
    img = qr.make_image(fill_color="black", back_color="white")
    
    # Convert to base64
    buffer = BytesIO()
    img.save(buffer, format="PNG")
    buffer.seek(0)
    
    return base64.b64encode(buffer.getvalue()).decode('utf-8')


def verify_totp(secret: str, code: str) -> bool:
    """
    Verify a TOTP code.
    Allows 1 period tolerance for clock drift.
    """
    if not secret or not code:
        return False
    
    # Remove spaces and normalize
    code = code.replace(" ", "").replace("-", "")
    
    # Must be 6 digits
    if not code.isdigit() or len(code) != 6:
        return False
    
    totp = pyotp.TOTP(secret)
    return totp.verify(code, valid_window=1)


# ==================== BACKUP CODES ====================

def generate_backup_codes() -> Tuple[List[str], str]:
    """
    Generate backup codes for account recovery.
    Returns (list of codes, hashed codes string for storage)
    """
    codes = []
    for _ in range(BACKUP_CODES_COUNT):
        # Generate random code
        code = secrets.token_hex(BACKUP_CODE_LENGTH // 2).upper()
        # Format as XXXX-XXXX
        formatted = f"{code[:4]}-{code[4:]}"
        codes.append(formatted)
    
    # Store as comma-separated for simplicity
    # In production, these should be hashed individually
    stored = ",".join(codes)
    
    return codes, stored


def verify_backup_code(stored_codes: str, code: str) -> Tuple[bool, Optional[str]]:
    """
    Verify a backup code.
    Returns (is_valid, remaining_codes_string)
    """
    if not stored_codes or not code:
        return False, stored_codes
    
    # Normalize code
    code = code.upper().replace(" ", "")
    if "-" not in code and len(code) == 8:
        code = f"{code[:4]}-{code[4:]}"
    
    codes = stored_codes.split(",")
    
    if code in codes:
        # Remove used code
        codes.remove(code)
        return True, ",".join(codes) if codes else None
    
    return False, stored_codes


def get_backup_codes_count(stored_codes: str) -> int:
    """Get number of remaining backup codes"""
    if not stored_codes:
        return 0
    return len(stored_codes.split(","))


# ==================== 2FA STATUS ====================

def format_secret_for_manual_entry(secret: str) -> str:
    """Format secret for manual entry (groups of 4)"""
    return " ".join([secret[i:i+4] for i in range(0, len(secret), 4)])
