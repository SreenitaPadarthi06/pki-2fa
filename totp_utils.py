import base64
import pyotp

def hex_to_base32(hex_seed: str) -> str:
    """Convert 64-char hex seed -> base32 string required by TOTP libs."""
    return base64.b32encode(bytes.fromhex(hex_seed)).decode()

def generate_totp(hex_seed: str) -> str:
    """Return current 6-digit TOTP code as string (SHA-1, 30s, 6 digits)."""
    seed = hex_to_base32(hex_seed)
    totp = pyotp.TOTP(seed, digits=6, interval=30)
    return totp.now()

def verify_totp(hex_seed: str, code: str) -> bool:
    """Verify code with ±1 period tolerance (valid_window=1)."""
    seed = hex_to_base32(hex_seed)
    totp = pyotp.TOTP(seed, digits=6, interval=30)
    return bool(totp.verify(code, valid_window=1))
