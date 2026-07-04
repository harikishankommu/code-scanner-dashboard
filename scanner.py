import subprocess
import json
import sys
from pathlib import Path


def run_bandit_scan(path="sample_project"):
    target = Path(path)

    if target.is_file():
        command = [
            sys.executable,
            "-m",
            "bandit",
            str(target),
            "-f",
            "json"
        ]
    else:
        command = [
            sys.executable,
            "-m",
            "bandit",
            "-r",
            str(target),
            "-f",
            "json"
        ]

    result = subprocess.run(
        command,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="ignore"
    )

    try:
        data = json.loads(result.stdout)
    except json.JSONDecodeError:
        return []

    issues = []

    for item in data.get("results", []):
        issues.append({
            "tool": "Bandit",
            "severity": item.get("issue_severity", "UNKNOWN"),
            "file": item.get("filename", "unknown"),
            "line": item.get("line_number", "-"),
            "message": item.get("issue_text", "No description")
        })

    return issues


def run_semgrep_scan(path="sample_project"):
    command = [
        "semgrep",
        "scan",
        "--config",
        "p/python",
        "--json",
        str(path)
    ]

    result = subprocess.run(
        command,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="ignore"
    )

    try:
        data = json.loads(result.stdout)
    except json.JSONDecodeError:
        return []

    issues = []

    for item in data.get("results", []):
        severity = item.get("extra", {}).get("severity", "INFO")

        if severity == "ERROR":
            severity = "HIGH"
        elif severity == "WARNING":
            severity = "MEDIUM"
        elif severity == "INFO":
            severity = "LOW"

        issues.append({
            "tool": "Semgrep",
            "severity": severity.upper(),
            "file": item.get("path", "unknown"),
            "line": item.get("start", {}).get("line", "-"),
            "message": item.get("extra", {}).get("message", "No description")
        })

    return issues


def run_all_scans(path="sample_project"):
    bandit_results = run_bandit_scan(path)
    semgrep_results = run_semgrep_scan(path)
    return bandit_results + semgrep_results


def count_by_severity(issues):
    counts = {
        "critical": 0,
        "high": 0,
        "medium": 0,
        "low": 0
    }

    for issue in issues:
        severity = issue["severity"].upper()

        if severity == "CRITICAL":
            counts["critical"] += 1
        elif severity in ["HIGH", "ERROR"]:
            counts["high"] += 1
        elif severity in ["MEDIUM", "WARNING"]:
            counts["medium"] += 1
        elif severity in ["LOW", "INFO"]:
            counts["low"] += 1

    return counts