import bcrypt
print(bcrypt.hashpw("soporte2025".encode("utf-8"), bcrypt.gensalt(rounds=12)).decode("utf-8"))
