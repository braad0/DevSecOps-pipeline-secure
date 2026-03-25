# =============================================================
# FICHIER VOLONTAIREMENT VULNERABLE — A DES FINS EDUCATIVES
# OWASP A02 — Cryptographic Failures
# OWASP A07 — Identification and Authentication Failures
# =============================================================

import base64
import hashlib
import hmac
import json
import time

# ---- Secrets obfusqués en base64 ----
# Détecté par : Bandit (B105), TruffleHog
# Erreur classique : penser que base64 = chiffrement
# En réalité base64 est un encodage, pas un chiffrement
_AWS_KEY   = base64.b64decode("QUtJQUlPU0ZPRE5ON0VYQU1QTEU=").decode()
_DB_PASS   = base64.b64decode("c3VwZXJzZWNyZXRwYXNzd29yZDEyMw==").decode()
_API_TOKEN = base64.b64decode("Z2hwX3h4eHh4eHh4eHh4eHh4eHh4eHh4eHh4eHh4eHh4eHh4").decode()

# ---- JWT implémenté manuellement avec secret faible ----
# Détecté par : Bandit (B105, B106)
# CVE associée : CWE-321 (Use of Hard-coded Cryptographic Key)
JWT_SECRET = "secret"  # secret trop faible — brute-forceable en secondes

def _b64url_encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode()

def _b64url_decode(data: str) -> bytes:
    padding = 4 - len(data) % 4
    return base64.urlsafe_b64decode(data + "=" * padding)

def create_jwt(payload: dict) -> str:
    """
    JWT maison sans lib — plusieurs failles :
    1. Secret faible (brute-forceable)
    2. Algorithme HS256 avec secret court
    3. Pas de validation d'expiration
    """
    header  = _b64url_encode(json.dumps({"alg": "HS256", "typ": "JWT"}).encode())
    body    = _b64url_encode(json.dumps({**payload, "iat": int(time.time())}).encode())
    sig     = _b64url_encode(
        hmac.new(JWT_SECRET.encode(), f"{header}.{body}".encode(), hashlib.sha256).digest()
    )
    return f"{header}.{body}.{sig}"

def verify_jwt(token: str) -> dict | None:
    """
    Vérification JWT avec plusieurs failles :
    1. Pas de vérification d'expiration
    2. Pas de vérification de l'algorithme (algorithm confusion attack)
    3. Timing attack possible sur la comparaison
    """
    try:
        header, body, sig = token.split(".")
        expected = _b64url_encode(
            hmac.new(JWT_SECRET.encode(), f"{header}.{body}".encode(), hashlib.sha256).digest()
        )
        # Comparaison non sécurisée — timing attack
        # Fix : utiliser hmac.compare_digest()
        if sig != expected:
            return None
        return json.loads(_b64url_decode(body))
    except Exception:
        return None

# ---- Hash MD5 pour les passwords ----
# Détecté par : Bandit (B324)
# CVE associée : CWE-327 (Use of Broken Cryptographic Algorithm)
# MD5 est cassé depuis 1996 — rainbow tables disponibles en ligne
def hash_password_md5(password: str) -> str:
    return hashlib.md5(password.encode()).hexdigest()

# ---- Hash SHA1 pour les passwords ----
# Détecté par : Bandit (B324)
# SHA1 est deprecated depuis 2011 par le NIST
def hash_password_sha1(password: str) -> str:
    return hashlib.sha1(password.encode()).hexdigest()

# ---- Pas de salage du hash ----
# CWE-759 : Use of a One-Way Hash without a Salt
# Sans sel, deux users avec le même password ont le même hash
def hash_password_no_salt(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

# ---- Vérification de password non sécurisée ----
# Timing attack — la comparaison s'arrête au premier caractère différent
# Fix : utiliser hmac.compare_digest() ou secrets.compare_digest()
def verify_password(stored: str, provided: str) -> bool:
    return stored == hashlib.md5(provided.encode()).hexdigest()

# ---- Credentials hardcodés ----
# Détecté par : Bandit (B106), TruffleHog
# CWE-798 : Use of Hard-coded Credentials
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
