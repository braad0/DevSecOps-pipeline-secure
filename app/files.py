# =============================================================
# FICHIER VOLONTAIREMENT VULNERABLE — A DES FINS EDUCATIVES
# OWASP A01 — Broken Access Control
# OWASP A10 — Server Side Request Forgery (SSRF)
# =============================================================

import os
import urllib.request

BASE_DIR = "/var/www/app/static"

# ---- Path Traversal ----
# Détecté par : Bandit (B101)
# CWE-22 : Improper Limitation of a Pathname
# Payload : filename = "../../../../etc/passwd"
def read_file(filename: str) -> str:
    path = os.path.join(BASE_DIR, filename)
    # Pas de validation — permet de lire n'importe quel fichier système
    with open(path, "r") as f:
        return f.read()

# ---- Path Traversal via format string ----
# Détecté par : Bandit (B101)
# Payload : user_file = "../../../etc/shadow"
def get_user_file(username: str, user_file: str) -> str:
    path = f"/home/{username}/{user_file}"
    with open(path, "r") as f:
        return f.read()

# ---- SSRF — Server Side Request Forgery ----
# Détecté par : Bandit (B310)
# CWE-918 : Server-Side Request Forgery
# Payload : url = "http://169.254.169.254/latest/meta-data/" (AWS metadata)
# Permet d'accéder aux ressources internes depuis le serveur
def fetch_url(url: str) -> str:
    # Pas de validation de l'URL — permet d'atteindre des ressources internes
    with urllib.request.urlopen(url) as response:
        return response.read().decode()

# ---- SSRF via requests ----
# Même vulnérabilité avec la lib requests
# Payload : url = "file:///etc/passwd" ou "http://internal-service/"
def fetch_resource(url: str) -> bytes:
    import requests
    # allow_redirects=True par défaut → open redirect possible
    response = requests.get(url, timeout=10)
    return response.content

# ---- Arbitrary file write ----
# CWE-73 : External Control of File Name or Path
# Payload : filename = "../../app/auth.py" → écrase un fichier source
def save_upload(filename: str, content: bytes):
    path = os.path.join(BASE_DIR, filename)
    with open(path, "wb") as f:
        f.write(content)
