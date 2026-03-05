import bcrypt
password = "soporte2025"
hash = "$2b$12$wbjtSXjG0hJwEXR2OrsDjemZu/nn/cp2rBb.2eEUbnvVpX3JLrx2a"
try:
    match = bcrypt.checkpw(password.encode('utf-8'), hash.encode('utf-8'))
    print(f"Match: {match}")
except Exception as e:
    print(f"Error: {e}")
