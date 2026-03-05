
import bcrypt

hashed = "$2b$12$wbjtSXjG0hJwEXR2OrsDjemZu/nn/cp2rBb.2eEUbnvVpX3JLrx2a"
password = "soporte2025"

if bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8')):
    print("MATCH: La contraseña coincide con el hash.")
else:
    print("NO MATCH: La contraseña NO coincide con el hash.")
