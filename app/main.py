# =============================================================
# FICHIER VOLONTAIREMENT VULNERABLE — A DES FINS EDUCATIVES
# Point d'entrée Flask avec SSTI
# OWASP A03 — Injection (SSTI)
# =============================================================

import os
import subprocess
from flask import Flask, request, render_template_string
from app.auth import create_jwt, verify_jwt, hash_password_md5
from app.database import get_user, login
from app.files import read_file, fetch_url

app = Flask(__name__)

# ---- SSTI — Server Side Template Injection ----
# Détecté par : Bandit (B703, B701)
# CWE-94 : Improper Control of Generation of Code
# Payload : name = "{{7*7}}" → affiche 49
# Payload RCE : name = "{{config.__class__.__init__.__globals__['os'].popen('id').read()}}"
@app.route("/hello")
def hello():
    name = request.args.get("name", "world")
    template = f"<h1>Hello {name}</h1>"
    return render_template_string(template)

# ---- Command Injection ----
# Détecté par : Bandit (B605, B602)
# CWE-78 : OS Command Injection
# Payload : filename = "; cat /etc/passwd"
@app.route("/ping")
def ping():
    host = request.args.get("host", "localhost")
    result = os.popen(f"ping -c 1 {host}").read()
    return result

# ---- Open Redirect ----
# CWE-601 : URL Redirection to Untrusted Site
# Payload : url = "https://evil.com"
@app.route("/redirect")
def redirect_user():
    url = request.args.get("url", "/")
    from flask import redirect
    return redirect(url)

# ---- Debug mode activé ----
# Détecté par : Bandit (B201)
# Ne jamais activer debug=True en production
# Expose un shell interactif dans le navigateur
if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
