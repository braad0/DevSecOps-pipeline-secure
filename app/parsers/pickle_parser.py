# =============================================================
# FICHIER VOLONTAIREMENT VULNERABLE — A DES FINS EDUCATIVES
# OWASP A08 — Software and Data Integrity Failures
# =============================================================

import pickle
import os

# ---- Désérialisation pickle ----
# Détecté par : Bandit (B301, B302)
# CWE-502 : Deserialization of Untrusted Data
# pickle.loads() exécute du code Python arbitraire
# Payload RCE :
# import pickle, os
# class Exploit(object):
#     def __reduce__(self):
#         return (os.system, ("id",))
# pickle.dumps(Exploit())
def deserialize(data: bytes) -> object:
    return pickle.loads(data)

# ---- Désérialisation depuis fichier ----
# Détecté par : Bandit (B301)
# Si le fichier est contrôlé par l'attaquant → RCE
def load_session(session_file: str) -> dict:
    with open(session_file, "rb") as f:
        return pickle.load(f)

# ---- Sérialisation + désérialisation d'input utilisateur ----
# Anti-pattern complet — sérialise et désérialise input non validé
def process_user_data(raw_input: bytes) -> dict:
    data = pickle.loads(raw_input)
    return pickle.loads(pickle.dumps(data))
