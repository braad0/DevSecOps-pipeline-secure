## README — DevSecOps-pipeline-secure

Application démonstrative d’un pipeline DevSecOps intégrant des contrôles de sécurité (SAST, SCA, secrets scanning, lint) avec GitHub Actions, et une application Python volontairement vulnérable à des fins pédagogiques. Le pipeline génère un rapport de sécurité consolidé (JSON + Markdown) en artefacts de build.

## Sommaire
* Présentation
* Architecture du projet
* Prérequis
* Installation
* Exécution locale
* Endpoints de l’application
* Scripts et outils
* Configuration
* Tests
* CI/CD — GitHub Actions
* Sécurité et vulnérabilités connues (intentionnelles)
* Roadmap
* Licence

## Présentation
Ce projet illustre:
* Comment mettre en place une chaîne DevSecOps avec GitHub Actions:
    * SAST avec Bandit
    * SCA des dépendances avec pip-audit
    * Scan de secrets avec TruffleHog
    * Linting avec flake8
    * Agrégation des résultats et génération d’un rapport
* Une application Flask minimale avec des composants intentionnellement vulnérables (YAML/XML parsing non sécurisé, désérialisation Pickle, SQL non paramétré, etc.) servant de base pour les démonstrations de détection et de remédiation.

Public visé: équipes sécurité, développeurs, DevOps souhaitant pratiquer la mise en place d’une pipeline de sécurité et comprendre des vulnérabilités courantes dans un cadre contrôlé.

## Architecture du projet
```
DevSecOps-pipeline-secure/
├── .github/
│   └── workflows/
│       └── security.yml
├── app/
│   ├── parsers/
│   │   ├── pickle_parser.py
│   │   └── yaml_parser.py
│   ├── main.py
│   ├── auth.py
│   ├── database.py
│   ├── files.py
│   └── requirements.txt
├── scripts/
│   └── generate_report.py
├── tests/
│   └── test_main.py
└── README.md

```

## Prérequis
* Python 3.10 à 3.12
* Pip et venv
* SQLite (embarqué avec Python, aucun service externe requis)
* GitHub Actions activé sur le dépôt pour exécuter la CI

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

## Exécution locale
L’application Flask écoute par défaut sur 0.0.0.0:5000 en mode debug.

* Lancer l’application:
    * python -m app.main
    * ou: python app/main.py
* Exemple rapide:
    * curl "http://localhost:5000/hello?name=world"

Attention:
* Le code est intentionnellement vulnérable (ne pas exposer en production).
* Les endpoints ci-dessous servent à des démonstrations encadrées.

## Endpoints de l’application
| Endpoint | Méthode | Params | Description |
|---|---|---|---|
| /hello | GET | name | Rend une page Hello avec le nom fourni (vulnérable à template injection si mal utilisé) |
| /ping | GET | host | Exécute une commande ping système et renvoie la sortie (risque d’injection de commande) |
| /redirect | GET | url | Redirige vers l’URL fournie (open redirect) |

Fonctions Python exposées pour les tests unitaires:
* calculate(expr: str) -> int
* check_admin(password: str) -> bool
* hash_password(password: str) -> str

## Scripts et outils
* scripts/generate_report.py
    * Agrège:
        * reports/bandit-results.sarif (Bandit)
        * reports/pip-audit-results.json (pip-audit)
    * Génère:
        * security-report.json
        * security-report.md
    * Lit le contexte CI via variables d’environnement:
        * GITHUB_SHA, GITHUB_REPOSITORY
        * SAST_STATUS, SCA_STATUS, SECRETS_STATUS, LINT_STATUS

## Configuration
Variables d’environnement utiles en CI (injectées par le workflow):
* SAST_STATUS, SCA_STATUS, SECRETS_STATUS, LINT_STATUS
* GITHUB_SHA, GITHUB_REPOSITORY

Application:
* L’app telle que fournie ne nécessite pas de variables pour démarrer.
* auth.py contient JWT_SECRET codé en dur pour la démo. Ne PAS reproduire.

Base de données:
* database.py utilise SQLite avec DB_PATH = "users.db"
* Exemple d’initialisation minimale de la base pour expérimenter:
    * sqlite3 users.db "CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, username TEXT, password TEXT, email TEXT);"
    * sqlite3 users.db "CREATE TABLE IF NOT EXISTS pending_updates (user_id INTEGER, email TEXT);"
    * sqlite3 users.db "INSERT INTO users (username, password, email) VALUES ('admin','admin1234','admin@example.com');"

## Tests
* Lancer les tests localement:
    * pytest -q
* Avec couverture (si pytest-cov installé localement):
    * pytest --cov=app --cov-report=term-missing

Le jeu de tests vérifie:
* calculate("1 + 1") == 2
* check_admin("admin1234") == True
* hash_password("password") retourne un hash hexadécimal MD5 sur 32 caractères

## CI/CD — GitHub Actions
Le workflow .github/workflows/security.yml orchestre 5 jobs:

1) SAST — Bandit
* Exécute Bandit sur app/
* Produit un rapport SARIF uploadé dans l’onglet Security
* Gate “High severity” bloquant

2) SCA — pip-audit
* Audite app/requirements.txt
* Échoue si des vulnérabilités sont détectées
* Exporte pip-audit-results.json en artefact

3) Secrets — TruffleHog
* Scanne l’historique pour secrets (only-verified)

4) Lint — flake8
* Vérifie le style Python (non bloquant dans ce setup — tolère les erreurs avec || true)

5) Report — Agrégation
* Télécharge les artefacts Bandit et pip-audit
* Exécute scripts/generate_report.py
* Publie security-report.json et security-report.md en artefacts

Sorties CI principales:
* Onglet Security: rapport SARIF Bandit
* Artefacts:
    * bandit-report-3.12/bandit-results.sarif
    * pip-audit-report/pip-audit-results.json
    * security-report/security-report.json
    * security-report/security-report.md

## Sécurité et vulnérabilités connues (intentionnelles)
Ce repo est volontairement vulnérable pour l’apprentissage. Ne JAMAIS l’utiliser en production.

Points saillants:
* Parsers
    * YAML: usage de yaml.load et Loader non sûrs (risques d’exécution arbitraire)
    * Pickle: loads sur données non fiables (RCE)
    * XML: parsers avec resolve_entities=True et payload Billion Laughs (XXE/DoS)
* Web
    * /hello: render_template_string avec données non échappées (template injection)
    * /ping: os.popen avec interpolation utilisateur (injection de commande)
    * /redirect: redirection ouverte (open redirect)
* Authentification
    * JWT_SECRET statique et faible
    * Hash de mots de passe en MD5/SHA1 et sans sel
    * Identifiants admin codés en dur
* Base de données
    * Concaténation de chaînes dans les requêtes SQL (SQL injection)
* Fichiers et réseau
    * Lecture de chemins construits depuis l’entrée (risques de path traversal)
    * Récupération d’URL arbitraires (SSRF)
* Dépendances
    * Versions anciennes/vulnérables (Flask 0.12.2, PyYAML 3.13, etc.) pour que SCA détecte des CVE

Ces vulnérabilités sont intentionnelles pour illustrer la détection par le pipeline et les approches de remédiation.

## Roadmap
* Ajouter un job Pytest dédié dans la CI pour exécuter les tests unitaires
* Fournir des exemples d’attaques contrôlées et leurs mitigations
* Ajouter des badges (CI, licence)
* Étendre la couverture de tests
* Ajouter un Dockerfile + scan d’images (Trivy)

## Licence
À définir (MIT recommandé pour un projet démo). Indiquer la licence choisie dans ce fichier et ajouter un badge dans l’en-tête du README.