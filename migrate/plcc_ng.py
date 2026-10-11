"""Convert plcc-ng's legacy dev-docs/issues/ tracker into Backlog.md files.

Usage: python3 -m migrate.plcc_ng --repo PLCC_NG --tracker ISSUES --triage FILE --report OUT
"""
import argparse
import json
import posixpath
import re
import sys
from pathlib import Path

from migrate.emit import (CORE_TYPES, TYPE_MAP, WONTDO_RE, assemble_description, filename_for,
                          render_task)
from migrate.legacy import parse_issue
from migrate.links import IssueRef, LinkContext, rewrite_issue_body

PROJECT = "plcc-ng"
OFFSET = 0
DUP_OFFSET = 400
DUP_RANGE = range(400, 500)
OTHER_OFFSETS = {"languages-ng": 500, "plcc-ng-demo": 800}
GITHUB = "https://github.com/ourPLCC/plcc-ng"
PROVENANCE_PREFIX = f"Migrated from {PROJECT} #"
PROVENANCE_END_RE = re.compile(
    rf"^{re.escape(PROVENANCE_PREFIX)}\d+\.\n<!-- SECTION:DESCRIPTION:END -->$", re.MULTILINE)
FOLDERS = ("tasks", "completed", "drafts")


def load_issues(repo_root):
    repo_root = Path(repo_root)
    base = repo_root / "dev-docs" / "issues"
    paths = sorted(base.glob("[0-9]*.md")) + sorted((base / "done").glob("[0-9]*.md"))
    issues = [parse_issue(p, repo_root) for p in paths]
    return sorted(issues, key=lambda i: (i.number, posixpath.basename(i.rel_path)))


def assign_ids(issues, offset=OFFSET, dup_offset=DUP_OFFSET, dup_range=DUP_RANGE):
    by_number = {}
    for issue in issues:
        by_number.setdefault(issue.number, []).append(issue)
    ids, remaps = {}, []
    for number, group in by_number.items():
        if len(group) > 2:
            raise SystemExit(f"#{number:03d} is used by {len(group)} files; extend the remap rule")
        ids[group[0].rel_path] = number + offset
        if len(group) == 2:
            cr = number + offset + dup_offset
            if cr not in dup_range:
                raise SystemExit(f"duplicate #{number:03d} remaps to CR-{cr}, outside the reserved "
                                 f"CR-{dup_range.start}..CR-{dup_range.stop - 1} range")
            ids[group[1].rel_path] = cr
            remaps.append(f"#{number:03d} {group[1].slug} -> CR-{cr} "
                          f"(#{number:03d} {group[0].slug} keeps CR-{number + offset})")
    return ids, remaps


def build_refs(issues, ids):
    refs = {}
    for issue in issues:
        refs.setdefault(issue.number, []).append(IssueRef(issue.slug, ids[issue.rel_path]))
    return refs


def issue_refs(issues):
    return build_refs(issues, assign_ids(issues)[0])


def _stem(issue):
    return posixpath.splitext(posixpath.basename(issue.rel_path))[0]


def _duplicated(issues):
    numbers = [issue.number for issue in issues]
    return {number for number in numbers if numbers.count(number) > 1}


def _triage_entry(table, issue, duplicated):
    """The entry keyed by the issue's file stem, else by its number unless that is duplicated."""
    if _stem(issue) in table:
        return table[_stem(issue)]
    return None if issue.number in duplicated else table.get(str(issue.number))


def _placement(issue, triage, duplicated):
    if issue.closed:
        return "completed"
    entry = _triage_entry(triage["open"], issue, duplicated)
    return "drafts" if entry["as"] == "draft" else "tasks"


def expected_counts(issues, triage):
    duplicated = _duplicated(issues)
    counts = {folder: 0 for folder in FOLDERS}
    for issue in issues:
        counts[_placement(issue, triage, duplicated)] += 1
    return counts


def _validate(issues, triage):
    errors = []
    duplicated = _duplicated(issues)
    open_triage = triage.get("open", {})
    overrides = triage.get("type_overrides", {})
    for name, table in (("open", open_triage), ("type_overrides", overrides)):
        for number in sorted(duplicated):
            if str(number) in table:
                stems = ", ".join(_stem(i) for i in issues if i.number == number)
                errors.append(f"{name} key {str(number)!r} is ambiguous; key by file stem ({stems})")
    for issue in issues:
        if not issue.closed:
            entry = _triage_entry(open_triage, issue, duplicated)
            if not entry or entry.get("as") not in ("cr", "draft"):
                errors.append(f"#{issue.number:03d} is open but has no valid triage entry")
        mapped = _triage_entry(overrides, issue, duplicated) or TYPE_MAP.get(issue.type)
        if mapped not in CORE_TYPES:
            errors.append(f"#{issue.number:03d} has type {issue.type!r}; add a type_overrides entry")
    if errors:
        raise SystemExit("cannot convert:\n  " + "\n  ".join(errors))


def is_migrated(path):
    """True if the file's description ends with this migration's provenance line."""
    return PROVENANCE_END_RE.search(path.read_text(encoding="utf-8")) is not None


def _remove_previous(backlog):
    for folder in FOLDERS:
        for path in (backlog / folder).glob("*.md"):
            if is_migrated(path):
                path.unlink()


def convert(repo_root, tracker_root, triage):
    repo_root, backlog = Path(repo_root), Path(tracker_root) / "backlog"
    issues = load_issues(repo_root)
    _validate(issues, triage)
    ids, remaps = assign_ids(issues)
    duplicated = _duplicated(issues)
    ctx = LinkContext(PROJECT, repo_root, build_refs(issues, ids), OTHER_OFFSETS, GITHUB)
    overrides = triage.get("type_overrides", {})
    _remove_previous(backlog)

    type_notes, wontdo, drafts, draft_number = [], [], [], 0
    for issue in issues:
        folder = _placement(issue, triage, duplicated)
        cr_type = _triage_entry(overrides, issue, duplicated) or TYPE_MAP[issue.type]
        if cr_type != issue.type:
            type_notes.append(f"#{issue.number:03d}: {issue.type!r} -> {cr_type}")
        labels, final_summary, status = [], None, "To Do"
        if folder == "completed":
            task_id, status = f"CR-{ids[issue.rel_path]}", "Done"
            if WONTDO_RE.match(issue.status_note):
                labels = ["wontdo"]
                note = rewrite_issue_body(issue.status_note, posixpath.dirname(issue.rel_path), ctx)
                final_summary = f"Abandoned before migration: {note}"
                wontdo.append(f"#{issue.number:03d} -> {task_id}: {issue.status_note}")
        elif folder == "drafts":
            draft_number += 1
            task_id = f"DRAFT-{draft_number}"
            drafts.append(f"#{issue.number:03d} -> {task_id}: {issue.title}")
        else:
            task_id = f"CR-{ids[issue.rel_path]}"
            status = _triage_entry(triage["open"], issue, duplicated).get("status", "To Do")
        body = rewrite_issue_body(assemble_description(issue), posixpath.dirname(issue.rel_path), ctx)
        description = f"{body}\n\n{PROVENANCE_PREFIX}{issue.number:03d}."
        text = render_task(task_id=task_id, title=issue.title, status=status, created=issue.date,
                           labels=labels, description=description, type_=cr_type,
                           project=PROJECT, final_summary=final_summary)
        (backlog / folder / filename_for(task_id, issue.title)).write_text(text, encoding="utf-8")

    counts = expected_counts(issues, triage)
    sections = [
        ("Duplicate-number remaps", remaps),
        ("Type mappings (non-identity)", type_notes),
        ("Won't-do (abandoned or superseded)", wontdo),
        ("Drafts (lose their number; provenance line keeps it greppable)", drafts),
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
