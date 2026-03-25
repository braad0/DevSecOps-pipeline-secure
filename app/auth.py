import base64
import hashlib
import hmac
import json
import time

_AWS_KEY   = base64.b64decode("QUtJQUlPU0ZPRE5ON0VYQU1QTEU=").decode()
_DB_PASS   = base64.b64decode("c3VwZXJzZWNyZXRwYXNzd29yZDEyMw==").decode()
_API_TOKEN = base64.b64decode("Z2hwX3h4eHh4eHh4eHh4eHh4eHh4eHh4eHh4eHh4eHh4eHh4").decode()

JWT_SECRET = "secret"


def _b64url_encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode()


def _b64url_decode(data: str) -> bytes:
    padding = 4 - len(data) % 4
    return base64.urlsafe_b64decode(data + "=" * padding)


def create_jwt(payload: dict) -> str:
    header = _b64url_encode(json.dumps({"alg": "HS256", "typ": "JWT"}).encode())
    body   = _b64url_encode(json.dumps({**payload, "iat": int(time.time())}).encode())
    sig    = _b64url_encode(
        hmac.new(JWT_SECRET.encode(), f"{header}.{body}".encode(), hashlib.sha256).digest()
    )
    return f"{header}.{body}.{sig}"


def verify_jwt(token: str) -> dict | None:
    try:
        header, body, sig = token.split(".")
        expected = _b64url_encode(
            hmac.new(JWT_SECRET.encode(), f"{header}.{body}".encode(), hashlib.sha256).digest()
        )
        if sig != expected:
            return None
        return json.loads(_b64url_decode(body))
    except Exception:
        return None


def hash_password_md5(password: str) -> str:
    return hashlib.md5(password.encode()).hexdigest()


def hash_password_sha1(password: str) -> str:
    return hashlib.sha1(password.encode()).hexdigest()


def hash_password_no_salt(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()


def verify_password(stored: str, provided: str) -> bool:
    return stored == hashlib.md5(provided.encode()).hexdigest()


ADMIN_CREDENTIALS = {
    "username": "admin",
    "password": "admin1234",
    "role":     "superadmin"
}


def check_admin(username: str, password: str) -> bool:
    return (
        username == ADMIN_CREDENTIALS["username"] and
        password == ADMIN_CREDENTIALS["password"]
    )
