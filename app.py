
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import os
import base64
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import serialization, hashes
from totp_utils import generate_totp, verify_totp

app = FastAPI()

ENCRYPTED_SEED = "/app/encrypted_seed.txt"
STUDENT_PRIVATE_KEY = "/app/student_private.pem"
OUTPUT_SEED_FILE = "/data/seed.txt"

class Code(BaseModel):
    code: str

def decrypt_seed():
    # read base64 encrypted_seed.txt, decode, then decrypt using RSA-OAEP-SHA256
    if not os.path.exists(ENCRYPTED_SEED):
        raise Exception("Encrypted seed file missing")

    if not os.path.exists(STUDENT_PRIVATE_KEY):
        raise Exception("Private key missing")

    with open(ENCRYPTED_SEED, "r") as f:
        enc_b64 = f.read().strip()

    try:
        encrypted = base64.b64decode(enc_b64)
    except Exception:
        raise Exception("Encrypted seed not base64")

    with open(STUDENT_PRIVATE_KEY, "rb") as f:
        private_key = serialization.load_pem_private_key(
            f.read(),
            password=None
        )

    try:
        seed_bytes = private_key.decrypt(
            encrypted,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
    except Exception:
        raise Exception("Seed decryption failed")

    hex_seed = seed_bytes.decode("utf-8")
    if len(hex_seed) != 64:
        raise Exception("Invalid seed length")

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

    code = generate_totp(hex_seed)
    return {"code": code}


@app.post("/verify-2fa")
def verify_2fa(c: Code):
    if not c.code:
        raise HTTPException(status_code=400, detail="Missing code")

    if not os.path.exists(OUTPUT_SEED_FILE):
        raise HTTPException(status_code=500, detail="Seed not decrypted yet")

    with open(OUTPUT_SEED_FILE, "r") as f:
        hex_seed = f.read().strip()

    valid = verify_totp(hex_seed, c.code)
    return {"valid": valid}

