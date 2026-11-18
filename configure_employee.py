"""Gera configuração privada; não salva senha em código ou arquivo automaticamente."""
import getpass
import hashlib
import re
import secrets


if __name__ == "__main__":
    pin = getpass.getpass("PIN de oito dígitos: ")
    if not re.fullmatch(r"[0-9]{8}", pin):
        raise SystemExit("Informe exatamente oito dígitos.")
    salt = secrets.token_bytes(16)
    digest = hashlib.pbkdf2_hmac("sha256", pin.encode(), salt, 600000)
    print("Configure estas variáveis privadas no servidor; não as publique:")
    print(f"EMPLOYEE_PIN_HASH=pbkdf2_sha256$600000${salt.hex()}${digest.hex()}")
    print(f"EMPLOYEE_SESSION_SECRET={secrets.token_urlsafe(48)}")
