from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import os
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import serialization, hashes

from totp_utils import generate_totp_code, verify_totp_code

app = FastAPI()

# Correct paths inside Docker
ENCRYPTED_SEED = "/app/encrypted_seed.txt"
STUDENT_PRIVATE_KEY = "/app/student_private.pem"
OUTPUT_SEED_FILE = "/data/seed.txt"

class Code(BaseModel):
    code: str

def decrypt_seed():
    """Decrypts encrypted_seed.txt and writes seed.txt into /data."""
    if not os.path.exists(ENCRYPTED_SEED):
        raise Exception("Encrypted seed file missing")

    if not os.path.exists(STUDENT_PRIVATE_KEY):
        raise Exception("Private key missing")

    # Load encrypted seed
    with open(ENCRYPTED_SEED, "rb") as f:
        encrypted = f.read()

    # Load private key
    with open(STUDENT_PRIVATE_KEY, "rb") as f:
        private_key = serialization.load_pem_private_key(
            f.read(),
            password=None
        )

    # Decrypt
    try:
        seed = private_key.decrypt(
            encrypted,
            padding.PKCS1v15()
        )
    except Exception:
        raise Exception("Seed decryption failed")

    # Convert bytes → hex
    hex_seed = seed.hex()

    # Store decrypted seed
    os.makedirs("/data", exist_ok=True)
    with open(OUTPUT_SEED_FILE, "w") as f:
        f.write(hex_seed)

    return True


@app.post("/decrypt-seed")
def decrypt_seed_endpoint():
    try:
        decrypt_seed()
        return {"status": "ok"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/generate-2fa")
def generate_2fa():
    if not os.path.exists(OUTPUT_SEED_FILE):
        raise HTTPException(status_code=500, detail="Seed not decrypted yet")

    with open(OUTPUT_SEED_FILE, "r") as f:
        hex_seed = f.read().strip()

    code = generate_totp_code(hex_seed)

    return {"code": code}


@app.post("/verify-2fa")
def verify_2fa(c: Code):
    if not c.code:
        raise HTTPException(status_code=400, detail="Missing code")

    if not os.path.exists(OUTPUT_SEED_FILE):
        raise HTTPException(status_code=500, detail="Seed not decrypted yet")

    with open(OUTPUT_SEED_FILE, "r") as f:
        hex_seed = f.read().strip()

    valid = verify_totp_code(hex_seed, c.code)
    return {"valid": valid}
