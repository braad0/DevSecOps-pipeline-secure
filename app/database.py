# =============================================================
# FICHIER VOLONTAIREMENT VULNERABLE — A DES FINS EDUCATIVES
# OWASP A03 — Injection
# =============================================================

import sqlite3

DB_PATH = "users.db"

# ---- SQL Injection basique ----
# Détecté par : Bandit (B608)
# CWE-89 : Improper Neutralization of SQL Commands
# Payload : user_id = "1 OR 1=1"
def get_user(user_id: str):
    conn  = sqlite3.connect(DB_PATH)
    query = "SELECT * FROM users WHERE id = " + user_id
    return conn.execute(query).fetchall()

# ---- SQL Injection via f-string ----
# Détecté par : Bandit (B608)
# Payload : username = "' OR '1'='1"
def get_user_by_name(username: str):
    conn  = sqlite3.connect(DB_PATH)
    query = f"SELECT * FROM users WHERE username = '{username}'"
    return conn.execute(query).fetchall()

# ---- SQL Injection dans DELETE ----
# Détecté par : Bandit (B608)
# Payload : user_id = "1 OR 1=1" → supprime TOUS les users
def delete_user(user_id: str):
    conn  = sqlite3.connect(DB_PATH)
    query = "DELETE FROM users WHERE id = " + user_id
    conn.execute(query)
    conn.commit()

# ---- SQL Injection dans LOGIN ----
# Détecté par : Bandit (B608)
# Payload classique : username="admin'--" password="anything"
# Le -- commente le reste de la requête → bypass complet
def login(username: str, password: str) -> bool:
    conn  = sqlite3.connect(DB_PATH)
    query = (
        f"SELECT * FROM users "
        f"WHERE username='{username}' "
        f"AND password='{password}'"
    )
    return conn.execute(query).fetchone() is not None

# ---- Second Order SQL Injection ----
# CWE-89 : La donnée est stockée "proprement" mais réutilisée dangereusement
def update_email(user_id: str, email: str):
    conn  = sqlite3.connect(DB_PATH)
    # Stockage : paramétré (correct)
    conn.execute(
        "INSERT INTO pending_updates (user_id, email) VALUES (?, ?)",
        (user_id, email)
    )
    # Réutilisation : non paramétré (dangereux)
    pending = conn.execute(
        "SELECT email FROM pending_updates WHERE user_id = " + user_id
    ).fetchone()
    if pending:
        conn.execute(
            f"UPDATE users SET email = '{pending[0]}' WHERE id = {user_id}"
        )
    conn.commit()
