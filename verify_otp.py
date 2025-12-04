from totp_utils import verify_totp

with open("data/seed.txt", "r") as f:
    hex_seed = f.read().strip()

code = input("Enter 6-digit code to verify: ").strip()
if len(code) != 6 or not code.isdigit():
    print("Invalid code format (must be 6 digits)")
    exit(1)

valid = verify_totp(hex_seed, code)
print("valid:", valid)
