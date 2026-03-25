# =============================================================
# FICHIER VOLONTAIREMENT VULNERABLE — A DES FINS EDUCATIVES
# OWASP A08 — Software and Data Integrity Failures
# =============================================================

import yaml

# ---- yaml.load() sans Loader ----
# Détecté par : Bandit (B506)
# CWE-502 : Deserialization of Untrusted Data
# yaml.load() peut exécuter du code Python arbitraire
# Payload :
# !!python/object/apply:os.system ["rm -rf /"]
def load_config_unsafe(yaml_string: str) -> dict:
    return yaml.load(yaml_string)

# ---- yaml.load() avec Loader=Loader ----
# Toujours dangereux — Loader permet l'exécution de code
def load_config_full_loader(yaml_string: str) -> dict:
    return yaml.load(yaml_string, Loader=yaml.Loader)

# ---- yaml.load() depuis un fichier ----
# Détecté par : Bandit (B506)
def load_config_from_file(path: str) -> dict:
    with open(path, "r") as f:
        return yaml.load(f)
