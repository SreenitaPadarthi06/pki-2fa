#!/usr/bin/env python3

import sys
import os
import datetime

# Ensure /app is in Python path for cron
sys.path.insert(0, "/app")

from totp_utils import generate_totp

SEED_FILE = "/data/seed.txt"
OUT_FILE = "/cron/last_code.txt"

try:
    if not os.path.exists(SEED_FILE):
        raise FileNotFoundError("seed not found")

    with open(SEED_FILE, "r") as f:
        hex_seed = f.read().strip()

    code = generate_totp(hex_seed)
    timestamp = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")

    with open(OUT_FILE, "a") as out:
        out.write(f"{timestamp} - 2FA Code: {code}\n")

except Exception as e:
    with open("/cron/cron_error.log", "a") as err:
        err.write(str(e) + "\n")
