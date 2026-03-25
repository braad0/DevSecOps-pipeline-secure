import json
import os
from datetime import datetime, timezone


def load_json(path: str) -> dict | list | None:
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return None


def parse_bandit(sarif_path: str) -> dict:
    data = load_json(sarif_path)
    if not data:
        return {"status": "no_data", "high": 0, "medium": 0, "low": 0, "findings": []}

    high = medium = low = 0
    findings = []

    for run in data.get("runs", []):
        for result in run.get("results", []):
            level = result.get("level", "").lower()
            rule_id = result.get("ruleId", "")
            message = result.get("message", {}).get("text", "")

            locations = result.get("locations", [])
            location = ""
            if locations:
                loc = locations[0].get("physicalLocation", {})
                file_path = loc.get("artifactLocation", {}).get("uri", "")
                line = loc.get("region", {}).get("startLine", "")
                location = f"{file_path}:{line}"

            if level == "error":
                high += 1
            elif level == "warning":
                medium += 1
            else:
                low += 1

            findings.append({
                "rule_id":  rule_id,
                "level":    level,
                "message":  message,
                "location": location,
            })

    status = "passed" if high == 0 else "failed"
    return {
        "status":   status,
        "high":     high,
        "medium":   medium,
        "low":      low,
        "findings": findings,
    }


def parse_pip_audit(json_path: str) -> dict:
    data = load_json(json_path)
    if not data:
        return {"status": "no_data", "total": 0, "vulnerabilities": []}

    vulns = []
    for dep in data.get("dependencies", []):
        for v in dep.get("vulns", []):
            vulns.append({
                "package": dep.get("name", ""),
                "version": dep.get("version", ""),
                "id":      v.get("id", ""),
                "description": v.get("description", "")[:100],
            })

    status = "passed" if not vulns else "failed"
    return {
        "status":          status,
        "total":           len(vulns),
        "vulnerabilities": vulns,
    }


def compute_verdict(sast: str, sca: str, secrets: str, lint: str) -> str:
    if any(s == "failure" for s in [sast, sca, secrets, lint]):
        return "FAILED"
    if any(s == "no_data" for s in [sast, sca, secrets, lint]):
        return "PARTIAL"
    return "PASSED"


def generate_markdown(report: dict) -> str:
    now        = report["metadata"]["generated_at"]
    commit     = report["metadata"]["commit"]
    repo       = report["metadata"]["repository"]
    verdict    = report["verdict"]
    bandit     = report["sast"]
    pip_audit  = report["sca"]
    sast_st    = report["pipeline"]["sast"]
    sca_st     = report["pipeline"]["sca"]
    secrets_st = report["pipeline"]["secrets"]
    lint_st    = report["pipeline"]["lint"]

    def badge(status: str) -> str:
        if status in ("success", "passed"):   return "PASSED"
        if status in ("failure", "failed"):   return "FAILED"
        return "UNKNOWN"

    lines = [
        "# Security Report",
        "",
        f"Date       : {now}",
        f"Commit     : {commit}",
        f"Repository : {repo}",
        f"Verdict    : {verdict}",
        "",
        "---",
        "",
        "## Résumé",
        "",
        "| Outil | Statut | Findings |",
        "|---|---|---|",
        f"| Bandit (SAST) | {badge(sast_st)} | "
        f"{bandit['high']} HIGH, {bandit['medium']} MEDIUM, {bandit['low']} LOW |",
        f"| pip-audit (SCA) | {badge(sca_st)} | "
        f"{pip_audit['total']} vulnérabilités |",
        f"| TruffleHog (Secrets) | {badge(secrets_st)} | - |",
        f"| flake8 (Lint) | {badge(lint_st)} | - |",
        "",
        "---",
        "",
    ]

    # Détail Bandit
    lines += [
        "## Détail Bandit",
        "",
    ]
    if bandit["findings"]:
        lines += [
            "| Règle | Sévérité | Localisation | Message |",
            "|---|---|---|---|",
        ]
        for f in bandit["findings"]:
            lines.append(
                f"| {f['rule_id']} | {f['level'].upper()} | "
                f"`{f['location']}` | {f['message'][:60]} |"
            )
    else:
        lines.append("Aucune vulnérabilité détectée.")
    lines.append("")
    lines.append("---")
    lines.append("")

    # Détail pip-audit
    lines += [
        "## Détail pip-audit",
        "",
    ]
    if pip_audit["vulnerabilities"]:
        lines += [
            "| Package | Version | CVE | Description |",
            "|---|---|---|---|",
        ]
        for v in pip_audit["vulnerabilities"]:
            lines.append(
                f"| {v['package']} | {v['version']} | "
                f"{v['id']} | {v['description']} |"
            )
    else:
        lines.append("Aucune vulnérabilité détectée.")
    lines.append("")
    lines.append("---")
    lines.append("")

    lines += [
        "## Avertissement",
        "",
        "Ce rapport a été généré automatiquement par le pipeline CI/CD.",
        "Le projet analysé est volontairement vulnérable à des fins éducatives.",
    ]

    return "\n".join(lines)


def main():
    # Récupérer les variables d'environnement GitHub Actions
    commit     = os.environ.get("GITHUB_SHA", "unknown")[:7]
    repository = os.environ.get("GITHUB_REPOSITORY", "unknown")
    sast_st    = os.environ.get("SAST_STATUS",    "unknown")
    sca_st     = os.environ.get("SCA_STATUS",     "unknown")
    secrets_st = os.environ.get("SECRETS_STATUS", "unknown")
    lint_st    = os.environ.get("LINT_STATUS",    "unknown")

    # Parser les rapports
    bandit    = parse_bandit("reports/bandit-results.sarif")
    pip_audit = parse_pip_audit("reports/pip-audit-results.json")

    # Verdict global
    verdict = compute_verdict(sast_st, sca_st, secrets_st, lint_st)

    # Construire le rapport
    report = {
        "metadata": {
            "generated_at": datetime.now(timezone.utc)
                            .replace(microsecond=0)
                            .isoformat()
                            .replace("+00:00", "Z"),
            "commit":     commit,
            "repository": repository,
            "version":    "1.0",
        },
        "verdict": verdict,
        "pipeline": {
            "sast":    sast_st,
            "sca":     sca_st,
            "secrets": secrets_st,
            "lint":    lint_st,
        },
        "sast": bandit,
        "sca":  pip_audit,
    }

    # Sauvegarder JSON
    with open("security-report.json", "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

    # Sauvegarder Markdown
    with open("security-report.md", "w", encoding="utf-8") as f:
        f.write(generate_markdown(report))

    print(f"Verdict       : {verdict}")
    print(f"Bandit        : {bandit['high']} HIGH, "
          f"{bandit['medium']} MEDIUM, {bandit['low']} LOW")
    print(f"pip-audit     : {pip_audit['total']} vulnérabilités")
    print(f"Report saved  : security-report.json + security-report.md")


if __name__ == "__main__":
    main()
