import sys
sys.path.append("/app")

import sys
import os
sys.path.append(os.path.abspath("/app"))

#!/usr/bin/env python3
import datetime
import os
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
    import sys
    sys.stderr.write(str(e) + "\n")
