"""Convert languages-ng's legacy dev-docs/issues/ tracker into Backlog.md files.

Usage: python3 -m migrate.languages_ng --repo LANGUAGES_NG --tracker TRACKER --triage FILE --report OUT
"""
import argparse
import json
import posixpath
import re
import sys
from pathlib import Path

from migrate.emit import (CORE_TYPES, TYPE_MAP, assemble_description, filename_for,
                          render_task, tracker_type)
from migrate.legacy import parse_frontmatter_issue
from migrate.links import IssueRef, LinkContext, rewrite_issue_body

PROJECT = "languages-ng"
OFFSET = 500
TARGETS = {"this repo": "languages-ng", "ourPLCC/plcc-ng": "plcc-ng"}
OTHER_OFFSETS = {"plcc-ng": 0, "plcc-ng-demo": 800}
GITHUB = "https://github.com/ourPLCC/languages-ng"
PROVENANCE_PREFIX = f"Migrated from {PROJECT} #"
PROVENANCE_END_RE = re.compile(
    rf"^{re.escape(PROVENANCE_PREFIX)}\d+\.\n<!-- SECTION:DESCRIPTION:END -->$", re.MULTILINE)
FOLDERS = ("tasks", "completed", "drafts")
AS_FOLDER = {"cr": "tasks", "draft": "drafts", "wontdo": "completed"}
TRIAGE_TABLES = ("open", "duplicates", "type_overrides", "references")
DRAFT_FILE_RE = re.compile(r"^draft-(\d+) - ")


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


def is_migrated(path):
    """True if the file's description ends with this migration's provenance line."""
    return PROVENANCE_END_RE.search(path.read_text(encoding="utf-8")) is not None


def _remove_previous(backlog):
    for folder in FOLDERS:
        for path in (backlog / folder).glob("*.md"):
            if is_migrated(path):
                path.unlink()


def _highest_draft(backlog):
    """The highest DRAFT-N number already in the tracker's drafts/, or 0."""
    numbers = [int(m.group(1)) for path in (backlog / "drafts").glob("draft-*.md")
               if (m := DRAFT_FILE_RE.match(path.name))]
    return max(numbers, default=0)


def _rewrite_bodies(repo_root, issues, triage):
    """Rewrite every issue's description; return (bodies by number, the link context)."""
    ctx = LinkContext(PROJECT, Path(repo_root), issue_refs(issues), OTHER_OFFSETS, GITHUB,
                      references=triage.get("references", {}))
    bodies = {}
    for issue in issues:
        ctx.source = str(issue.number)
        bodies[issue.number] = rewrite_issue_body(
            assemble_description(issue), posixpath.dirname(issue.rel_path), ctx)
    return bodies, ctx


def unresolved_references(repo_root, triage):
    """Bare #N references that are neither a languages-ng issue nor decided in triage."""
    return _rewrite_bodies(repo_root, load_issues(repo_root), triage)[1].unresolved


def convert(repo_root, tracker_root, triage):
    repo_root, backlog = Path(repo_root), Path(tracker_root) / "backlog"
    issues = load_issues(repo_root)
    dup_types = validate(issues, triage, backlog)
    bodies, ctx = _rewrite_bodies(repo_root, issues, triage)
    _remove_previous(backlog)

    duplicates, overrides = triage.get("duplicates", {}), triage.get("type_overrides", {})
    dup_notes, type_notes, wontdo, drafts = [], [], [], []
    draft_number = _highest_draft(backlog)
    for issue in issues:
        key, folder = str(issue.number), _placement(issue, triage)
        task_id, status, labels, final_summary = f"CR-{issue.number + OFFSET}", "Done", [], None
        if key in duplicates:
            cr_type = dup_types[issue.number]
            labels = ["wontdo"]
            final_summary = f"Duplicate of CR-{duplicates[key]}, filed upstream by hand."
            dup_notes.append(f"#{issue.number:03d} -> {task_id}: duplicate of CR-{duplicates[key]}")
        else:
            cr_type = overrides.get(key) or TYPE_MAP[issue.type]
            entry = {} if issue.closed else triage["open"][key]
            if entry.get("as") == "wontdo":
                labels, final_summary = ["wontdo"], entry["summary"]
                wontdo.append(f"#{issue.number:03d} -> {task_id}: {entry['summary']}")
            elif folder == "drafts":
                draft_number += 1
                task_id, status = f"DRAFT-{draft_number}", "To Do"
                drafts.append(f"#{issue.number:03d} -> {task_id}: {issue.title}")
            elif folder == "tasks":
                status = entry.get("status", "To Do")
        if cr_type != issue.type:
            type_notes.append(f"#{issue.number:03d}: {issue.type!r} -> {cr_type}")
        description = f"{bodies[issue.number]}\n\n{PROVENANCE_PREFIX}{issue.number:03d}."
        text = render_task(task_id=task_id, title=issue.title, status=status, created=issue.date,
                           labels=labels, description=description, type_=cr_type,
                           project=TARGETS[issue.target], final_summary=final_summary)
        (backlog / folder / filename_for(task_id, issue.title)).write_text(text, encoding="utf-8")

    counts = expected_counts(issues, triage)
    sections = [
        ("Duplicates of plcc-ng issues", dup_notes),
        ("Type mappings (non-identity)", type_notes),
        ("Won't-do (obsolete)", wontdo),
        ("Drafts (lose their number; provenance line keeps it greppable)", drafts),
        ("Unresolved #N references (add a references entry to the triage file)", ctx.unresolved),
        ("Defaulted #N references (unqualified #N read as a languages-ng issue)", ctx.defaulted),
        ("Link findings", ctx.findings),
    ]
    lines = [f"# {PROJECT} migration report", "",
             f"Converted {len(issues)} files: {counts['completed']} -> completed/, "
             f"{counts['tasks']} -> tasks/, {counts['drafts']} -> drafts/.", ""]
    for title, items in sections:
        lines += [f"## {title}", ""] + ([f"- {item}" for item in items] or ["(none)"]) + [""]
    return "\n".join(lines)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--repo", required=True, type=Path)
    parser.add_argument("--tracker", required=True, type=Path)
    parser.add_argument("--triage", required=True, type=Path)
    parser.add_argument("--report", required=True, type=Path)
    args = parser.parse_args(argv)
    triage = json.loads(args.triage.read_text(encoding="utf-8"))
    report = convert(args.repo, args.tracker, triage)
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(report, encoding="utf-8")
    print(report.splitlines()[2])
    return 0


if __name__ == "__main__":
    sys.exit(main())
