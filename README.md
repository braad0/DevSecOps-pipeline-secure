
# DevSecOps Pipeline Secure

Pipeline CI/CD de sécurité automatisé — analyse statique, scan de secrets,
audit de dépendances et rapport de sécurité généré à chaque push.

---

## Présentation

J'ai construit ce pipeline pour démontrer comment intégrer la sécurité
directement dans le cycle de développement, avant que le code parte en production.
L'idée centrale c'est le **shift-left security** : détecter les vulnérabilités
le plus tôt possible dans le cycle CI/CD plutôt que de les découvrir en production.

Le pipeline analyse automatiquement le code source à chaque push sur `main`
et bloque le déploiement si des vulnérabilités critiques sont détectées.
Pour démontrer son fonctionnement, j'ai développé une application Python
volontairement vulnérable couvrant l'OWASP Top 10.

---

## Structure du projet

```
DevSecOps-pipeline-secure/
├── .github/
│   └── workflows/
│       └── security.yml        # Pipeline principal — 5 jobs (parallèles/agrégation)
├── app/
│   ├── main.py                 # App Flask — SSTI, command injection, open redirect
│   ├── auth.py                 # JWT faible, MD5/SHA1, secrets obfusqués en base64
│   ├── database.py             # SQL injection basique, f-string, second order
│   ├── files.py                # Path traversal, SSRF, arbitrary file write
│   ├── parsers/
│   │   ├── pickle_parser.py    # Désérialisation pickle → RCE
│   │   ├── yaml_parser.py      # yaml.load() non sécurisé → RCE
│   │   └── xml_parser.py       # XXE/Billion Laughs (DoS/lecture locale)
│   └── requirements.txt        # Dépendances volontairement vulnérables (CVEs connus)
├── scripts/
│   └── generate_report.py      # Agrégateur → rapport JSON + Markdown
├── tests/
│   └── test_main.py            # Tests unitaires de fonctions wrapper
└── README.md
```

---

## Comment ça marche

```
Push sur main
      ↓
┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐
│   SAST   │  │   SCA    │  │ Secrets  │  │   Lint   │
│  Bandit  │  │pip-audit │  │Trufflehog│  │  flake8  │
└────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘
     └─────────────┴──────────────┴─────────────┘
                             ↓
                     ┌───────────────┐
                     │    Report     │
                     │ JSON+Markdown │
                     └───────────────┘
```

Les 4 premiers jobs tournent en parallèle (Bandit en matrice Python 3.10/3.11/3.12).
Le job `report` attend leurs résultats et agrège tout dans un rapport final.

---

## Les 5 jobs du pipeline

| Job | Outil | Ce qu'il détecte | Security Gate |
|---|---|---|---|
| SAST | Bandit | Vulnérabilités dans le code source | Échoue si HIGH détecté |
| SCA | pip-audit | CVEs dans les dépendances | Échoue si CVE trouvé |
| Secrets | TruffleHog | Secrets et tokens exposés | Échoue si secret vérifié |
| Lint | flake8 | Qualité et style du code | Informatif |
| Report | generate_report.py | Agrège tous les résultats | Toujours exécuté |

---

## L'application vulnérable — OWASP Top 10

Application Flask volontairement vulnérable pour produire des findings réalistes.

| Fichier | Vulnérabilité | OWASP | Détecté par |
|---|---|---|---|
| auth.py | JWT secret faible, MD5/SHA1, secrets base64, credentials codés | A02, A07 | Bandit |
| database.py | SQL injection (concat/f-strings), second-order | A03 | Bandit |
| files.py | Path traversal, SSRF, écriture arbitraire | A01, A10 | Bandit |
| main.py | SSTI (render_template_string), command injection (ping), open redirect, debug=True | A03, A05 | Bandit |
| pickle_parser.py | Désérialisation pickle → RCE | A08 | Bandit |
| yaml_parser.py | yaml.load(), FullLoader non sûrs → exécution arbitraire | A08 | Bandit |
| xml_parser.py | XXE (resolve_entities), Billion Laughs DoS | A05 | Bandit |
| requirements.txt | Versions vulnérables (Flask, PyYAML, Jinja2, etc.) | A06 | pip-audit |

Avertissement: ces vulnérabilités sont intentionnelles et à but éducatif. Ne pas déployer.

---

## Prérequis

* Python 3.10 à 3.12
* Pip et venv
* GitHub Actions activé sur le dépôt
* SQLite (embarqué avec Python, aucun service à installer)

---

## Installation

* Cloner le dépôt:
    * git clone https://github.com/<user>/DevSecOps-pipeline-secure.git
    * cd DevSecOps-pipeline-secure
* Créer un environnement virtuel:
    * Linux/macOS:
        * python -m venv .venv
        * source .venv/bin/activate
    * Windows (PowerShell):
        * python -m venv .venv
        * .venv\Scripts\Activate.ps1
* Installer les dépendances:
    * pip install -r app/requirements.txt

---

## Exécution locale

L’application Flask écoute par défaut sur 0.0.0.0:5000 en mode debug.

* Démarrer:
    * python -m app.main
    * ou: python app/main.py
* Exemples:
    * curl "http://localhost:5000/hello?name=world"
    * curl "http://localhost:5000/ping?host=localhost"
    * curl -i "http://localhost:5000/redirect?url=/hello"

Attention: ces endpoints sont vulnérables par conception. Usage local et contrôlé uniquement.

---

## Endpoints de l’application

| Endpoint | Méthode | Params | Description |
|---|---|---|---|
| /hello | GET | name | Affiche un message Hello. Utilise render_template_string (SSTI si non échappé) |
| /ping | GET | host | Exécute ping via shell (risque d’injection de commande) |
| /redirect | GET | url | Redirige vers l’URL fournie (open redirect) |

Fonctions Python exposées aux tests:
* calculate(expr: str) -> int
* check_admin(password: str) -> bool
* hash_password(password: str) -> str

---

## Base de données (démo)

Chemin par défaut: users.db

Initialisation minimale pour expérimenter:
* sqlite3 users.db "CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, username TEXT, password TEXT, email TEXT);"
* sqlite3 users.db "CREATE TABLE IF NOT EXISTS pending_updates (user_id INTEGER, email TEXT);"
* sqlite3 users.db "INSERT INTO users (username, password, email) VALUES ('admin','admin1234','admin@example.com');"

Note: les requêtes dans database.py sont non paramétrées (SQLi intentionnelle).

---

## Scripts et artefacts

* scripts/generate_report.py
    * Entrées:
        * reports/bandit-results.sarif (Bandit, format SARIF)
        * reports/pip-audit-results.json (pip-audit)
    * Sorties:
        * security-report.json
        * security-report.md
    * Contexte CI:
        * GITHUB_SHA, GITHUB_REPOSITORY
        * SAST_STATUS, SCA_STATUS, SECRETS_STATUS, LINT_STATUS

Artefacts CI publiés:
* bandit-report-3.12/bandit-results.sarif
* pip-audit-report/pip-audit-results.json
* security-report/security-report.json
* security-report/security-report.md

---

## Configuration

Application:
* Aucune variable obligatoire pour démarrer en local.
* auth.py contient JWT_SECRET en clair pour la démo (ne pas reproduire).

CI:
* Les statuts des jobs (SAST/SCA/Secrets/Lint) sont injectés via variables d’environnement par le workflow et repris dans le rapport.

---

## Tests

* Exécuter les tests:
    * pytest -q
* Avec couverture:
    * pytest --cov=app --cov-report=term-missing

Ce que test_main.py vérifie:
* calculate("1 + 1") == 2
* check_admin("admin1234") est True, "wrongpassword" est False
* hash_password("password") renvoie un MD5 hex de 32 caractères

---

## Détails du workflow GitHub Actions

Chemin: .github/workflows/security.yml

1) SAST — Bandit
* Installation bandit[sarif]
* Scan récursif de app/
* Export SARIF pour l’onglet Security
* Gate bloquant sur sévérité High
2) SCA — pip-audit
* Audit de app/requirements.txt (ou de l’env si absent)
* Rapport JSON
* Gate: échec si au moins une vulnérabilité
3) Secrets — TruffleHog
* Scan de l’historique git
* Mode only-verified pour limiter les faux positifs
4) Lint — flake8
* max-line-length=120
* Informatif (ne casse pas le pipeline)
5) Report — Agrégation
* Télécharge les artefacts Bandit/pip-audit
* Exécute scripts/generate_report.py
* Publie security-report.json et security-report.md

---

## Sécurité et vulnérabilités connues (intentionnelles)

Ce repo est volontairement vulnérable pour l’apprentissage. Ne JAMAIS l’utiliser en production.

Points saillants:
* Parsers:
    * YAML: yaml.load / Loader non sûrs (exécution arbitraire)
    * Pickle: loads sur données non fiables (RCE)
    * XML: resolve_entities=True + Billion Laughs (XXE/DoS)
* Web:
    * /hello: render_template_string sur entrée utilisateur (SSTI)
    * /ping: os.popen avec interpolation directe (command injection)
    * /redirect: redirection non validée (open redirect)
* Auth:
    * JWT_SECRET faible et statique
    * Hash mots de passe en MD5/SHA1, sans sel
    * Identifiants admin codés en dur
* Base de données:
    * Concaténation de chaînes dans les requêtes (SQL injection)
    * Risque de second-order via pending_updates
* Fichiers et réseau:
    * Path traversal possible sur chemins construits
    * Récupération d’URL arbitraires (SSRF)
    * Écritures directes sur disque
* Dépendances:
    * Versions obsolètes et vulnérables (Flask 0.12.2, Jinja2 2.10, PyYAML 3.13, etc.)

---

## Bonnes pratiques de remédiation (pistes)

* Remplacer yaml.load par yaml.safe_load
* Interdire pickle.loads sur données non fiables (ou utiliser formats sûrs: JSON, msgpack)
* Désactiver XXE: parsers sans entités externes, defusedxml
* Éviter render_template_string avec données non contrôlées, échapper/filtrer strictement
* Remplacer os.popen par sous-processus avec liste d’arguments, valider l’input
* Valider et restreindre les redirections sortantes
* Paramétrer toutes les requêtes SQL (placeholders ?)
* Utiliser bcrypt/argon2 + sel pour les mots de passe
* Stocker secrets dans un secret manager (GitHub Secrets, Vault, etc.)
* Mettre à jour les dépendances, activer contraintes de version, renovate/dependabot
* Désactiver debug et limiter l’exposition réseau en prod

---

## Avertissement légal

Cet outil est destiné uniquement à des fins éducatives et à des analyses
sur des systèmes dont vous êtes propriétaire ou pour lesquels vous disposez
d'une autorisation écrite explicite. Toute utilisation non autorisée est
illégale. L'auteur décline toute responsabilité en cas d'utilisation
abusive de cet outil.
