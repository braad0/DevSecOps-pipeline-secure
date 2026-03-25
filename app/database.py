# =============================================================
# FICHIER VOLONTAIREMENT VULNERABLE — A DES FINS EDUCATIVES
# =============================================================

import sqlite3

# SQL Injection — concaténation directe de l'input utilisateur
# Détecté par : Bandit (B608)

def get_user(user_id):
    conn = sqlite3.connect("users.db")
    query = "SELECT * FROM users WHERE id = " + user_id
    return conn.execute(query)


def get_user_by_name(username):
    conn = sqlite3.connect("users.db")
    query = f"SELECT * FROM users WHERE username = '{username}'"
    return conn.execute(query)


def delete_user(user_id):
    conn = sqlite3.connect("users.db")
    query = "DELETE FROM users WHERE id = " + user_id
    conn.execute(query)
    conn.commit()


def login(username, password):
    conn = sqlite3.connect("users.db")
    # Double injection — username ET password non sanitisés
    query = f"SELECT * FROM users WHERE username='{username}' AND password='{password}'"
    result = conn.execute(query).fetchone()
    return result is not None
