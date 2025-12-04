import base64
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import hashes
import os

# Load private key
with open("student_private.pem", "rb") as f:
    private_key = serialization.load_pem_private_key(f.read(), password=None)

# Read encrypted seed
with open("encrypted_seed.txt", "r") as f:
    encrypted_seed_b64 = f.read().strip()

# Decode base64
encrypted_bytes = base64.b64decode(encrypted_seed_b64)

# Decrypt using private key
decrypted_bytes = private_key.decrypt(
    encrypted_bytes,
    padding.OAEP(
        mgf=padding.MGF1(algorithm=hashes.SHA256()),
        algorithm=hashes.SHA256(),
        label=None
    )
)

# Convert decrypted bytes to hex string
hex_seed = decrypted_bytes.decode("utf-8").strip()

# Validate 64-char hex
if len(hex_seed) != 64:
    raise ValueError("Invalid seed length: expected 64 hex characters")

# Create data folder if not exists
os.makedirs("data", exist_ok=True)

# Save decrypted seed
with open("data/seed.txt", "w") as f:
    f.write(hex_seed)

print("Seed decrypted and saved to data/seed.txt")
