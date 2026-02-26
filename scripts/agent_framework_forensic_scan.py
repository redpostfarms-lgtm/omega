#!/usr/bin/env python3
"""
Agent Framework Forensic Scan
- audits architecture for portability, community channel, profile files, and brain access
- scans targeted framework scripts/logs for placeholder markers
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPORT_DIR = ROOT / "audit_reports"
REPORT_DIR.mkdir(exist_ok=True)

TARGET_FILES = [
    ROOT / "unified_agent_framework.py",
    ROOT / "omega_agent_council.py",
    ROOT / "agents" / "development_agent.py",
    ROOT / "agents" / "communication_agent.py",
]

PROFILE_FILES = [
    ROOT / "config" / "agents" / "profiles" / "development_agent.json",
    ROOT / "config" / "agents" / "profiles" / "communication_agent.json",
]

COUNCIL_DIR = ROOT / "config" / "agent_council"
LOG_FILES = [
    ROOT / "logs" / "agents" / "town_hall.log",
    ROOT / "omega_agents" / "agent_states.json",
    ROOT / "omega_agents" / "learning_queue.json",
]

MARKERS = ["TODO", "FIXME", "PLACEHOLDER", "TBD", "mock", "stub"]


def scan_markers(path: Path):
    findings = []
    if not path.exists():
        return findings
    text = path.read_text(encoding="utf-8", errors="ignore")
    for i, line in enumerate(text.splitlines(), start=1):
        for marker in MARKERS:
            if marker in line:
                findings.append(f"{path.relative_to(ROOT)}:{i}: {line.strip()}")
                break
    return findings


def has_symbol(path: Path, symbol: str) -> bool:
    if not path.exists():
        return False
    return symbol in path.read_text(encoding="utf-8", errors="ignore")


def main() -> int:
    checks = {
        "framework_exists": (ROOT / "unified_agent_framework.py").exists(),
        "town_hall_api": has_symbol(ROOT / "unified_agent_framework.py", "def town_hall_post"),
        "agent_bundle_export": has_symbol(ROOT / "unified_agent_framework.py", "def export_agent_bundle"),
        "brain_access": has_symbol(ROOT / "unified_agent_framework.py", "class GatekeeperBrainAccess"),
        "council_profile_loader": has_symbol(ROOT / "omega_agent_council.py", "def _load_agent_profiles"),
        "dev_profile_file": PROFILE_FILES[0].exists(),
        "comm_profile_file": PROFILE_FILES[1].exists(),
        "council_profiles_count": len(list(COUNCIL_DIR.glob("*.json"))) if COUNCIL_DIR.exists() else 0,
    }

    marker_hits = []
    for file in TARGET_FILES:
        marker_hits.extend(scan_markers(file))

    report = {
        "generated_at": datetime.now().isoformat(),
        "checks": checks,
        "log_files_present": [str(p.relative_to(ROOT)) for p in LOG_FILES if p.exists()],
        "marker_hits": marker_hits,
        "status": "pass" if checks["framework_exists"] and checks["town_hall_api"] and checks["brain_access"] and checks["agent_bundle_export"] and checks["council_profile_loader"] and checks["dev_profile_file"] and checks["comm_profile_file"] else "fail",
    }

    ts = datetime.now().strftime("%Y%m%d-%H%M%S")
    out_json = REPORT_DIR / f"agent_framework_forensic_{ts}.json"
    out_md = REPORT_DIR / f"agent_framework_forensic_{ts}.md"
    out_json.write_text(json.dumps(report, indent=2), encoding="utf-8")

    md_lines = [
        "# Agent Framework Forensic Scan",
        f"Generated: {report['generated_at']}",
        "",
        "## Checks",
    ]
    for key, value in checks.items():
        md_lines.append(f"- {key}: {value}")
    md_lines.extend(["", "## Log Files Present"]) 
    if report["log_files_present"]:
        md_lines.extend([f"- {x}" for x in report["log_files_present"]])
    else:
        md_lines.append("- none")
    md_lines.extend(["", "## Marker Hits (targeted)"])
    if marker_hits:
        md_lines.extend([f"- {x}" for x in marker_hits])
    else:
        md_lines.append("- none")
    md_lines.extend(["", f"## Status", f"- {report['status']}"])

    out_md.write_text("\n".join(md_lines), encoding="utf-8")
    print(str(out_md))
    return 0 if report["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
