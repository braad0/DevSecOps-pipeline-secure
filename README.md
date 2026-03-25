
# devsecops-pipeline — Plan du projet

---

## Structure du projet

```
devsecops-pipeline/
├── .github/
│   └── workflows/
│       └── security.yml        # Pipeline principal
├── app/
│   ├── main.py                 # App volontairement vulnérable
│   ├── database.py             # SQL injection volontaire
│   ├── auth.py                 # Secrets exposés volontaires
│   └── requirements.txt        # Dépendances vulnérables
├── scripts/
│   └── generate_report.py      # Agrégateur → rapport JSON/Markdown
├── tests/
│   └── test_main.py
└── README.md
```

---

## Le pipeline — 5 jobs

```
security.yml
│
├── job: sast           (analyse statique)
│   └── Bandit → détecte eval(), exec(), SQLi, hardcoded passwords...
│       └── output SARIF → affiché dans GitHub Security tab
│
├── job: sca            (dépendances vulnérables)
│   └── pip-audit → détecte CVEs dans requirements.txt
│       └── échoue si CVSS > 7.0
│
├── job: secrets        (scan de secrets)
│   └── TruffleHog → scan du code ET de l'historique Git
│       └── échoue si secret trouvé
│
├── job: lint           (qualité de code)
│   └── flake8 → détecte les mauvaises pratiques Python
│
└── job: report         (dépend des 4 jobs précédents)
    └── generate_report.py → agrège tout
        └── rapport JSON + Markdown uploadé comme artefact
```

---

## Jobs en parallèle

```
push
  ↓
┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐
│  sast   │  │   sca   │  │ secrets │  │  lint   │
│ Bandit  │  │pip-audit│  │Trufflehg│  │ flake8  │
└────┬────┘  └────┬────┘  └────┬────┘  └────┬────┘
     └────────────┴────────────┴────────────┘
                              ↓
                        ┌─────────┐
                        │ report  │
                        │  JSON   │
                        │Markdown │
                        └─────────┘
```

---

## Security Gates — le pipeline échoue si

| Outil | Condition d'échec |
|---|---|
| Bandit | Vulnérabilité de sévérité HIGH détectée |
| pip-audit | CVE avec score CVSS > 7.0 |
| TruffleHog | Au moins un secret trouvé |
| flake8 | Erreurs critiques de syntaxe |

---

## Le projet vulnérable — ce qu'il contient

### `app/auth.py` — secrets exposés
```python
# Détecté par TruffleHog et Bandit
AWS_ACCESS_KEY = "AKIAIOSFODNN7EXAMPLE"
AWS_SECRET_KEY = "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"
DB_PASSWORD    = "supersecretpassword123"
API_TOKEN      = "ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
```

### `app/database.py` — SQL injection
```python
# Détecté par Bandit (B608)
def get_user(user_id):
    query = "SELECT * FROM users WHERE id = " + user_id
    return db.execute(query)
```

### `app/main.py` — code dangereux
```python
# Détecté par Bandit (B307, B102)
eval(user_input)
os.system(user_command)
subprocess.call(cmd, shell=True)
pickle.loads(data)
```

### `app/requirements.txt` — dépendances vulnérables
```
flask==0.12.2        # CVE-2018-1000656
requests==2.18.0     # CVE-2018-18074
pyyaml==3.13         # CVE-2017-18342
jinja2==2.10         # CVE-2019-10906
```

---

## `scripts/generate_report.py` — ce qu'il fait

```
1. Lit les outputs JSON de Bandit, pip-audit, TruffleHog
2. Agrège les résultats
3. Calcule un score de sécurité global
4. Génère un rapport Markdown lisible
5. Génère un rapport JSON structuré
6. Les deux sont uploadés comme artefacts GitHub Actions
```

---

## Rapport Markdown généré

```markdown
# Security Report — devsecops-pipeline

Date     : 2026-03-25
Commit   : a1b2c3d
Verdict  : FAILED

## Résumé

| Outil | Statut | Findings |
|---|---|---|
| Bandit | FAILED | 4 HIGH, 2 MEDIUM |
| pip-audit | FAILED | 3 CVEs critiques |
| TruffleHog | FAILED | 2 secrets trouvés |
| flake8 | PASSED | 0 erreurs |
```

---

## SARIF — intégration GitHub Security tab

```yaml
- name: Upload SARIF
  uses: github/codeql-action/upload-sarif@v3
  with:
    sarif_file: bandit-results.sarif
```

---

## Badge README

```markdown
![Security Pipeline](https://github.com/braad0/devsecops-pipeline/actions/workflows/security.yml/badge.svg)
```

---

## Matrice Python

```yaml
strategy:
  matrix:
    python-version: ["3.10", "3.11", "3.12"]
```

---

## Ce que ça démontre

| Feature | Compétence démontrée |
|---|---|
| Multi-jobs parallèles | Architecture CI/CD avancée |
| Security Gates | Shift-left security mindset |
| SARIF + GitHub Security | Intégration native GitHub |
| Rapport agrégé Python | Scripting DevSecOps |
| Matrice Python 3.10/3.11/3.12 | Bonnes pratiques CI/CD |
| Badge README | Professionnalisme |
| Projet vulnérable documenté | Compréhension des vulnérabilités |

