
# DevSecOps Pipeline Secure

Pipeline CI/CD de sécurité automatisé — SAST, SCA, scan de secrets, lint — avec rapport consolidé à chaque push.


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

## Vue d’ensemble

Ce repo contient:
* Un pipeline GitHub Actions avec 5 jobs (SAST, SCA, Secrets, Lint, Report)
* Une application Flask volontairement vulnérable (OWASP Top 10) pour la démo

```mermaid
flowchart LR
    A[Push sur main] --> B{Jobs parallèles}
    B --> C[SAST - Bandit]
    B --> D[SCA - pip-audit]
    B --> E[Secrets - TruffleHog]
    B --> F[Lint - flake8]
    C --> G[Report - Agrégation]
    D --> G
    E --> G
    F --> G
    G --> H[Artefacts: security-report.json / .md]
```

![Status CI](https://img.shields.io/github/actions/workflow/status/braad0/DevSecOps-pipeline-secure/security.yml?branch=main)
![Python](https://img.shields.io/badge/python-3.10%20|%203.11%20|%203.12-blue)

---

## Structure

```
DevSecOps-pipeline-secure/
├── .github/workflows/security.yml     # Pipeline sécurité (SAST, SCA, Secrets, Lint, Report)
├── app/
│   ├── main.py                        # Flask (SSTI, RCE ping, open redirect)
│   ├── auth.py                        # JWT faible, MD5/SHA1, secrets encodés
│   ├── database.py                    # SQL injection (concat/f-strings)
│   ├── files.py                       # Path traversal, SSRF, write arbitraire
│   ├── parsers/
│   │   ├── pickle_parser.py           # Désérialisation pickle → RCE
│   │   ├── yaml_parser.py             # yaml.load() non sécurisé → RCE
│   │   └── xml_parser.py              # XXE / Billion Laughs
│   └── requirements.txt               # Versions vulnérables pour SCA
├── scripts/generate_report.py         # Agrège → security-report.json/.md
├── tests/test_main.py                 # Tests unitaires (wrappers)
└── README.md
```

---

## Détails du pipeline

```mermaid
graph TB
    subgraph Parallèle
        B1[SAST<br/>Bandit<br/>SARIF]
        B2[SCA<br/>pip-audit<br/>JSON]
        B3[Secrets<br/>TruffleHog]
        B4[Lint<br/>flake8]
    end
    B1 --> R[Report<br/>scripts/generate_report.py]
    B2 --> R
    B3 --> R
    B4 --> R
    R --> A1((security-report.json))
    R --> A2((security-report.md))
```

Artefacts et sorties:
* reports/bandit-results.sarif
* reports/pip-audit-results.json
* security-report.json
* security-report.md

Captures recommandées:
* ![Onglet Security](assets/security-tab.png)
* ![Artefacts CI](assets/artifacts.png)
* ![Security report](assets/security-report.png)

---

## L’application vulnérable (OWASP Top 10)

```mermaid
flowchart LR
    U[Client] --> F[Flask app]
    F --> A[auth.py]
    F --> D[database.py]
    F --> FI[files.py]
    F --> P[parsers/]
    P --> P1[pickle_parser.py]
    P --> P2[yaml_parser.py]
    P --> P3[xml_parser.py]
    D --> DB[(users.db)]
```

| Zone | Fichier | Vulnérabilités (exemples) | OWASP |
|---|---|---|---|
| Auth | auth.py | JWT secret faible, MD5/SHA1, credentials codés | A02, A07 |
| DB | database.py | SQLi via concat/f-strings, second-order | A03 |
| Fichiers/Réseau | files.py | Path traversal, SSRF, write arbitraire | A01, A10 |
| Web | main.py | SSTI, injection de commande, open redirect, debug=True | A03, A05 |
| Parsers | pickle/yaml/xml | RCE pickle, yaml.load non sûr, XXE/Billion Laughs | A08 |
| Dépendances | requirements.txt | Versions obsolètes/vulnérables | A06 |

Avertissement: ce code est intentionnellement vulnérable. Ne pas exposer publiquement.

---

## Prérequis

* Python 3.10–3.12
* pip + venv
* GitHub Actions actif
* SQLite (embarqué)

---

## Installation

* git clone https://github.com/<user>/DevSecOps-pipeline-secure.git
* cd DevSecOps-pipeline-secure
* python -m venv .venv
* source .venv/bin/activate    (Windows: .venv\Scripts\Activate.ps1)
* pip install -r app/requirements.txt

---

## Lancer en local

* python -m app.main   (ou: python app/main.py)
* Exemples:
    * curl "http://localhost:5000/hello?name=world"
    * curl "http://localhost:5000/ping?host=localhost"
    * curl -i "http://localhost:5000/redirect?url=/hello"

Note: endpoints vulnérables par conception. Usage local/contrôlé uniquement.

---

## Base de données (démo)

```
sqlite3 users.db "CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, username TEXT, password TEXT, email TEXT);"
sqlite3 users.db "CREATE TABLE IF NOT EXISTS pending_updates (user_id INTEGER, email TEXT);"
sqlite3 users.db "INSERT INTO users (username, password, email) VALUES ('admin','admin1234','admin@example.com');"
```

---

## Tests

```
pytest -q
# ou avec couverture si installé:
pytest --cov=app --cov-report=term-missing
```

Vérifie:
* calculate("1 + 1") == 2
* check_admin("admin1234") == True
* hash_password("password") → MD5 hex 32 chars

---

## Extrait du rapport (exemple)

| Outil | Statut | Findings |
|---|---|---|
| Bandit (SAST) | FAILED | 5 HIGH, 18 MEDIUM, 5 LOW |
| pip-audit (SCA) | FAILED | 12 vulnérabilités |
| TruffleHog (Secrets) | PASSED | - |
| flake8 (Lint) | PASSED | - |

---

## Bonnes pratiques (pistes de remédiation)

```mermaid
%%{init: {
  "theme": "base",
  "themeVariables": {
    "background": "#ffffff",
    "primaryTextColor": "#0f172a",
    "lineColor": "#334155"
  }
}}%%
mindmap
  root((Remédiations)):::center
    Parsers:::grp1
      yaml.safe_load
      defusedxml
      éviter_pickle
    Web:::grp2
      échapper_filtrer
      pas_de_render_template_string
      subprocess_run_shell_false
    DB:::grp3
      requêtes_paramétrées
      validations_dentrée
    Auth:::grp4
      bcrypt_argon2_sel
      rotation_secrets
      JWT_clés_sûres
    Dépendances:::grp5
      pinning_updates
      Dependabot_Renovate
    Opérations:::grp6
      debug_False
      least_privilege
      secrets_manager

classDef center fill:#fde68a,stroke:#92400e,color:#111827,stroke-width:2px;
classDef grp1 fill:#cffafe,stroke:#0e7490,color:#0f172a,stroke-width:1.5px;
classDef grp2 fill:#e9d5ff,stroke:#6d28d9,color:#0f172a,stroke-width:1.5px;
classDef grp3 fill:#dcfce7,stroke:#15803d,color:#0f172a,stroke-width:1.5px;
classDef grp4 fill:#fee2e2,stroke:#b91c1c,color:#0f172a,stroke-width:1.5px;
classDef grp5 fill:#e0e7ff,stroke:#3730a3,color:#0f172a,stroke-width:1.5px;
classDef grp6 fill:#fef3c7,stroke:#a16207,color:#0f172a,stroke-width:1.5px;
```

Astuce: Si GitHub a encore du mal à rendre Mermaid, exporte ces diagrammes en SVG/PNG avec mermaid-cli et inclus-les comme images:
* ![Architecture de l’app](assets/app-arch.svg)
* ![Remédiations](assets/remediation.svg)

---

## Détails du workflow GitHub Actions

Fichier: .github/workflows/security.yml

1) SAST — Bandit
* Scan récursif app/, export SARIF (onglet Security)
* “Security Gate” High bloquant

2) SCA — pip-audit
* Audit de app/requirements.txt (ou l’environnement)
* Échec si CVE détecté
* Artefact JSON

3) Secrets — TruffleHog
* Scan historique (only-verified)

4) Lint — flake8
* max-line-length=120 (informatif)

5) Report — Agrégation
* Télécharge artefacts
* Exécute scripts/generate_report.py
* Publie security-report.json / .md

---

## Roadmap

* Ajouter un job Pytest dans la CI (matrice Python)
* Semgrep + règles custom
* CodeQL
* Trivy (si Dockerfile)
* SBOM CycloneDX
* Badges (CI, licence, Python)
* Plus de captures et de démos d’attaque/mitigation

---


