"""Convert languages-ng's legacy dev-docs/issues/ tracker into Backlog.md files.

Usage: python3 -m migrate.languages_ng --repo LANGUAGES_NG --tracker TRACKER --triage FILE --report OUT
"""
import re
from pathlib import Path

from migrate.emit import CORE_TYPES, TYPE_MAP
from migrate.legacy import parse_frontmatter_issue
from migrate.links import IssueRef

PROJECT = "languages-ng"
OFFSET = 500
TARGETS = {"this repo": "languages-ng", "ourPLCC/plcc-ng": "plcc-ng"}
OTHER_OFFSETS = {"plcc-ng": 0, "plcc-ng-demo": 800}
GITHUB = "https://github.com/ourPLCC/languages-ng"
FOLDERS = ("tasks", "completed", "drafts")
AS_FOLDER = {"cr": "tasks", "draft": "drafts", "wontdo": "completed"}
TRIAGE_TABLES = ("open", "duplicates", "type_overrides", "references")
TYPE_LINE_RE = re.compile(r"^type: (\S+)$", re.MULTILINE)


def load_issues(repo_root):
    repo_root = Path(repo_root)
    paths = sorted((repo_root / "dev-docs" / "issues").glob("[0-9]*.md"))
    return [parse_frontmatter_issue(path, repo_root) for path in paths]


def issue_refs(issues):
    return {issue.number: [IssueRef(issue.slug, issue.number + OFFSET)] for issue in issues}


def _placement(issue, triage):
    key = str(issue.number)
    if key in triage.get("duplicates", {}) or issue.closed:
        return "completed"
    return AS_FOLDER[triage["open"][key]["as"]]


def expected_counts(issues, triage):
    counts = dict.fromkeys(FOLDERS, 0)
    for issue in issues:
        counts[_placement(issue, triage)] += 1
    return counts


def tracker_type(backlog, cr):
    """The type of CR-<cr> in the tracker, or None if the tracker has no such CR."""
    for folder in ("tasks", "completed"):
        for path in (Path(backlog) / folder).glob(f"cr-{cr} - *.md"):
            found = TYPE_LINE_RE.search(path.read_text(encoding="utf-8"))
            return found.group(1) if found else None
    return None


def validate(issues, triage, backlog):
    """Return {legacy number: type} for the duplicates; exit listing every problem instead."""
    errors, dup_types = [], {}
    numbers = [issue.number for issue in issues]
    for number in sorted({n for n in numbers if numbers.count(n) > 1}):
        errors.append(f"#{number:03d} is used by more than one file; add a duplicate remap range")
    known = {str(n) for n in numbers}
    for table in TRIAGE_TABLES:
        for key in triage.get(table, {}):
            if key not in known:
                errors.append(f"{table} key {key!r} is not a languages-ng issue number")
    duplicates = triage.get("duplicates", {})
    for issue in issues:
        key = str(issue.number)
        if issue.target not in TARGETS:
            errors.append(f"#{issue.number:03d} has target {issue.target!r}; "
                          f"expected one of {sorted(TARGETS)}")
        if key in duplicates:
            dup_types[issue.number] = tracker_type(backlog, duplicates[key])
            if dup_types[issue.number] is None:
                errors.append(f"#{issue.number:03d} duplicates CR-{duplicates[key]}, "
                              f"which the tracker does not have")
            continue
        if not issue.closed:
            entry = triage.get("open", {}).get(key)
            if not entry or entry.get("as") not in AS_FOLDER:
                errors.append(f"#{issue.number:03d} is open but has no valid triage entry")
            elif entry["as"] == "wontdo" and not entry.get("summary"):
                errors.append(f"#{issue.number:03d} is triaged wontdo but has no summary")
        mapped = triage.get("type_overrides", {}).get(key) or TYPE_MAP.get(issue.type)
        if mapped not in CORE_TYPES:
            errors.append(f"#{issue.number:03d} has type {issue.type!r}; add a type_overrides entry")
    if errors:
        raise SystemExit("cannot convert:\n  " + "\n  ".join(errors))
    return dup_types
