from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import os
import pyotp
import time
from totp_utils import generate_totp, verify_totp

app = FastAPI()
SEED_FILE = "data/seed.txt"

class Code(BaseModel):
    code: str

@app.post("/decrypt-seed")
def decrypt_seed_endpoint():
    if not os.path.exists(SEED_FILE):
        raise HTTPException(status_code=500, detail="Seed not decrypted")
    return {"status": "ok"}

@app.get("/generate-2fa")
def generate_2fa():
    if not os.path.exists(SEED_FILE):
        raise HTTPException(status_code=500, detail="Seed not decrypted yet")

    with open(SEED_FILE, "r") as f:
        seed = f.read().strip()

    code = generate_totp(seed)
    valid_for = 30 - (int(time.time()) % 30)

    return {"code": code, "valid_for": valid_for}

@app.post("/verify-2fa")
def verify_2fa(c: Code):
    if not c.code:
        raise HTTPException(status_code=400, detail="Missing code")

    if not os.path.exists(SEED_FILE):
        raise HTTPException(status_code=500, detail="Seed not decrypted yet")

    with open(SEED_FILE, "r") as f:
        seed = f.read().strip()

    valid = verify_totp(seed, c.code)
    return {"valid": valid}
