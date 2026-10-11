"""Verify a converted tracker against its legacy source.

Usage: python3 -m migrate.verify --repo REPO --tracker TRACKER --triage FILE [--driver plcc-ng|languages-ng]
"""
import argparse
import json
import os
import re
import subprocess
import sys
from pathlib import Path

from migrate import drivers, plcc_ng

ID_RE = re.compile(r"^id: (\S+)$", re.MULTILINE)


def _frontmatter_id(text):
    """Return the id from the frontmatter, or None."""
    match = re.match(r"---\n(.*?)\n---\n", text, re.DOTALL)
    found = match and ID_RE.search(match.group(1))
    return found.group(1) if found else None


def _backlog(tracker_root, *args):
    env = dict(os.environ, BACKLOG_CWD=str(tracker_root))
    return subprocess.run(["backlog", *args], cwd=tracker_root, env=env,
                          capture_output=True, text=True)


def verify(repo_root, tracker_root, triage, driver=plcc_ng):
    tracker_root = Path(tracker_root)
    backlog = tracker_root / "backlog"
    errors = []
    expected = driver.expected_counts(driver.load_issues(repo_root), triage)
    migrated = {folder: [p for p in (backlog / folder).glob("*.md") if driver.is_migrated(p)]
                for folder in driver.FOLDERS}
    for folder in driver.FOLDERS:
        if len(migrated[folder]) != expected[folder]:
            errors.append(f"{folder}/: {len(migrated[folder])} migrated files, expected {expected[folder]}")
    if not list((backlog / "completed").glob("cr-999 - *.md")):
        errors.append("seed CR-999 missing from completed/")

    for path in migrated["tasks"] + migrated["completed"]:
        task_id = _frontmatter_id(path.read_text(encoding="utf-8"))
        if task_id is None:
            errors.append(f"{path.parent.name}/{path.name}: no id: line in frontmatter")
            continue
        result = _backlog(tracker_root, "task", "view", task_id, "--plain")
        if result.returncode != 0 or f"Task {task_id} " not in result.stdout:
            errors.append(f"backlog cannot view {task_id} ({path.name})")
    if migrated["drafts"]:
        listing = _backlog(tracker_root, "draft", "list", "--plain").stdout
        for path in migrated["drafts"]:
            draft_id = _frontmatter_id(path.read_text(encoding="utf-8"))
            if draft_id is None:
                errors.append(f"{path.parent.name}/{path.name}: no id: line in frontmatter")
                continue
            if draft_id not in listing:
                errors.append(f"backlog draft list does not show {draft_id}")

    doctor = _backlog(tracker_root, "doctor")
    if doctor.returncode != 0:
        errors.append(f"backlog doctor failed:\n{doctor.stdout}{doctor.stderr}")
    check = subprocess.run([sys.executable, str(tracker_root / "bin" / "check.py"),
                            "--root", str(tracker_root)], capture_output=True, text=True)
    if check.returncode != 0:
        errors.append(f"bin/check.py failed:\n{check.stderr}")
    if hasattr(driver, "unresolved_references"):
        errors += [f"unresolved reference, add a triage entry: {item}"
                   for item in driver.unresolved_references(repo_root, triage)]
    return errors


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--repo", required=True, type=Path)
    parser.add_argument("--tracker", required=True, type=Path)
    parser.add_argument("--triage", required=True, type=Path)
    parser.add_argument("--driver", choices=sorted(drivers.DRIVERS), default="plcc-ng")
    args = parser.parse_args(argv)
    errors = verify(args.repo, args.tracker, json.loads(args.triage.read_text(encoding="utf-8")),
                    drivers.load(args.driver))
    for error in errors:
        print(f"verify: {error}", file=sys.stderr)
    if errors:
        return 1
    print("verify: ok")
    return 0


if __name__ == "__main__":
    sys.exit(main())
