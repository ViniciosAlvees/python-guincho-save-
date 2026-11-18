"""PIN privado e sessões curtas, verificáveis entre instâncias serverless."""

import base64
import hashlib
import hmac
import os
import re
import secrets
import threading
import time
from datetime import datetime, timezone

from fastapi import HTTPException, Request

SESSION_SECONDS = 600
ATTEMPT_WINDOW = 300
MAX_ATTEMPTS = 5
_attempts = {}
_lock = threading.Lock()


def configuration():
    encoded = os.getenv("EMPLOYEE_PIN_HASH", "")
    secret = os.getenv("EMPLOYEE_SESSION_SECRET", "")
    try:
        algorithm, rounds, salt, digest = encoded.split("$")
        rounds = int(rounds)
        salt = bytes.fromhex(salt)
        digest = bytes.fromhex(digest)
        if (algorithm != "pbkdf2_sha256" or not 600000 <= rounds <= 2000000
                or len(salt) < 16 or len(digest) != 32 or len(secret) < 43):
            raise ValueError()
    except (ValueError, TypeError):
        raise HTTPException(503, "Acesso de funcionários não configurado.") from None
    # Alterar o PIN ou a chave também invalida as sessões anteriores.
    signing_key = hmac.digest(secret.encode(), encoded.encode(), "sha256")
    return rounds, salt, digest, signing_key


def login(pin, request: Request):
    rounds, salt, digest, signing_key = configuration()
    if not isinstance(pin, str) or not re.fullmatch(r"[0-9]{8}", pin):
        raise HTTPException(400, "Informe o PIN de oito dígitos.")
    # Limite adicional por instância; não depende de X-Forwarded-For fornecido pelo cliente.
    address = request.client.host if request.client else "unknown"
    now = int(time.time())
    with _lock:
        for key in list(_attempts):
            if _attempts[key][0] <= now - ATTEMPT_WINDOW:
                del _attempts[key]
        start, count = _attempts.get(address, (now, 0))
        if count >= MAX_ATTEMPTS or (len(_attempts) >= 10000 and address not in _attempts):
            raise HTTPException(429, "Muitas tentativas. Aguarde cinco minutos.",
                                headers={"Retry-After": str(ATTEMPT_WINDOW)})
        _attempts[address] = (start, count + 1)
    actual = hashlib.pbkdf2_hmac("sha256", pin.encode(), salt, rounds)
    if not hmac.compare_digest(actual, digest):
        raise HTTPException(401, "PIN inválido.")
    with _lock:
        _attempts.pop(address, None)
    expires = int(time.time()) + SESSION_SECONDS
    payload = expires.to_bytes(8, "big") + secrets.token_bytes(24)
    signature = hmac.digest(signing_key, b"employee-session-v1:" + payload, "sha256")
    token = base64.urlsafe_b64encode(payload + signature).decode().rstrip("=")
    return {"token": token, "expiresAt": datetime.fromtimestamp(
        expires, timezone.utc).isoformat().replace("+00:00", "Z")}


def require_employee(request: Request):
    authorization = request.headers.get("authorization", "")
    if not authorization.startswith("Bearer "):
        raise HTTPException(401, "Sessão de funcionário obrigatória.")
    token = authorization[7:]
    if not re.fullmatch(r"[A-Za-z0-9_-]{86}", token):
        raise HTTPException(401, "Sessão inválida ou expirada.")
    raw = base64.urlsafe_b64decode(token + "==")
    # Exige codificação canônica para evitar aliases do mesmo token.
    if base64.urlsafe_b64encode(raw).decode().rstrip("=") != token:
        raise HTTPException(401, "Sessão inválida ou expirada.")
    _, _, _, signing_key = configuration()
    payload, signature = raw[:32], raw[32:]
    expected = hmac.digest(signing_key, b"employee-session-v1:" + payload, "sha256")
    expires = int.from_bytes(payload[:8], "big")
    now = int(time.time())
    if (not hmac.compare_digest(signature, expected)
            or expires <= now or expires > now + SESSION_SECONDS):
        raise HTTPException(401, "Sessão inválida ou expirada.")

