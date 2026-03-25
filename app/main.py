# =============================================================
# FICHIER VOLONTAIREMENT VULNERABLE — A DES FINS EDUCATIVES
# =============================================================

import os
import subprocess
import pickle
from app.auth import AWS_ACCESS_KEY, DB_PASSWORD
from app.database import get_user, login


# eval() sur input utilisateur — exécution de code arbitraire
# Détecté par : Bandit (B307)
def calculate(expression):
    return eval(expression)


# os.system() avec input non sanitisé — command injection
# Détecté par : Bandit (B605)
def run_command(user_command):
    os.system(user_command)


# subprocess avec shell=True — command injection
# Détecté par : Bandit (B602)
def run_script(script_name):
    subprocess.call(f"python {script_name}", shell=True)


# pickle.loads() sur données non fiables — désérialisation dangereuse
# Détecté par : Bandit (B301)
def load_data(raw_bytes):
    return pickle.loads(raw_bytes)


# Mot de passe hardcodé
# Détecté par : Bandit (B105)
def check_admin(password):
    if password == "admin1234":
        return True
    return False


# MD5 pour hasher des passwords — algo faible
# Détecté par : Bandit (B324)
import hashlib
def hash_password(password):
    return hashlib.md5(password.encode()).hexdigest()


if __name__ == "__main__":
    print("AWS Key :", AWS_ACCESS_KEY)
    print("DB Pass :", DB_PASSWORD)
    print(calculate("1+1"))
