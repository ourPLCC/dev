"""Convert plcc-ng's legacy dev-docs/issues/ tracker into Backlog.md files.

Usage: python3 -m migrate.plcc_ng --repo PLCC_NG --tracker ISSUES --triage FILE --report OUT

plcc-ng-demo's tracker has the same format; migrate.plcc_ng_demo runs this
converter with its own Profile.
"""
import argparse
import json
import posixpath
import re
import sys
from dataclasses import dataclass
from pathlib import Path

from migrate.emit import (CORE_TYPES, TYPE_MAP, WONTDO_RE, assemble_description, filename_for,
                          render_task, tracker_type)
from migrate.legacy import parse_issue
from migrate.links import IssueRef, LinkContext, rewrite_issue_body

OFFSET = 0
DUP_OFFSET = 400
DUP_RANGE = range(400, 500)
FOLDERS = ("tasks", "completed", "drafts")
TRIAGE_TABLES = ("open", "type_overrides", "duplicates")
UPSTREAM = "plcc-ng"


@dataclass(frozen=True)
class Profile:
    """What differs between repos whose trackers use plcc-ng's format."""
    project: str
    offset: int
    dup_offset: int
    dup_range: range
    other_offsets: dict
    github: str

    @property
    def provenance_prefix(self):
        return f"Migrated from {self.project} #"

    @property
    def provenance_end_re(self):
        return re.compile(rf"^{re.escape(self.provenance_prefix)}\d+\.\n"
                          r"<!-- SECTION:DESCRIPTION:END -->$", re.MULTILINE)


PLCC_NG = Profile("plcc-ng", OFFSET, DUP_OFFSET, DUP_RANGE,
                  {"languages-ng": 500, "plcc-ng-demo": 800}, "https://github.com/ourPLCC/plcc-ng")


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


def _ids(issues, profile):
    return assign_ids(issues, profile.offset, profile.dup_offset, profile.dup_range)


def issue_refs(issues, profile=PLCC_NG):
    return build_refs(issues, _ids(issues, profile)[0])


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
    if issue.closed or _triage_entry(triage.get("duplicates", {}), issue, duplicated):
        return "completed"
    entry = _triage_entry(triage["open"], issue, duplicated)
    return "drafts" if entry["as"] == "draft" else "tasks"


def expected_counts(issues, triage):
    duplicated = _duplicated(issues)
    counts = {folder: 0 for folder in FOLDERS}
    for issue in issues:
        counts[_placement(issue, triage, duplicated)] += 1
    return counts


def _validate(issues, triage, backlog):
    """Return {rel_path: type} for the upstream duplicates; exit listing every problem instead."""
    errors, dup_types = [], {}
    duplicated = _duplicated(issues)
    open_triage = triage.get("open", {})
    overrides = triage.get("type_overrides", {})
    upstream = triage.get("duplicates", {})
    known = {str(i.number) for i in issues} | {_stem(i) for i in issues}
    for key in upstream:
        if key not in known:
            errors.append(f"duplicates key {key!r} is not a legacy issue number or file stem")
    for name in TRIAGE_TABLES:
        table = triage.get(name, {})
        for number in sorted(duplicated):
            if str(number) in table:
                stems = ", ".join(_stem(i) for i in issues if i.number == number)
                errors.append(f"{name} key {str(number)!r} is ambiguous; key by file stem ({stems})")
    for issue in issues:
        cr = _triage_entry(upstream, issue, duplicated)
        if cr:
            dup_types[issue.rel_path] = tracker_type(backlog, cr)
            if dup_types[issue.rel_path] is None:
                errors.append(f"#{issue.number:03d} duplicates CR-{cr}, which the tracker does not have")
            continue
        if not issue.closed:
            entry = _triage_entry(open_triage, issue, duplicated)
            if not entry or entry.get("as") not in ("cr", "draft"):
                errors.append(f"#{issue.number:03d} is open but has no valid triage entry")
        mapped = _triage_entry(overrides, issue, duplicated) or TYPE_MAP.get(issue.type)
        if mapped not in CORE_TYPES:
            errors.append(f"#{issue.number:03d} has type {issue.type!r}; add a type_overrides entry")
    if errors:
        raise SystemExit("cannot convert:\n  " + "\n  ".join(errors))
    return dup_types


def is_migrated(path, profile=PLCC_NG):
    """True if the file's description ends with this migration's provenance line."""
    return profile.provenance_end_re.search(path.read_text(encoding="utf-8")) is not None


def _remove_previous(backlog, profile):
    for folder in FOLDERS:
        for path in (backlog / folder).glob("*.md"):
            if is_migrated(path, profile):
                path.unlink()


def convert(repo_root, tracker_root, triage, profile=PLCC_NG):
    repo_root, backlog = Path(repo_root), Path(tracker_root) / "backlog"
    issues = load_issues(repo_root)
    dup_types = _validate(issues, triage, backlog)
    ids, remaps = _ids(issues, profile)
    duplicated = _duplicated(issues)
    ctx = LinkContext(profile.project, repo_root, build_refs(issues, ids), profile.other_offsets,
                      profile.github)
    overrides, upstream = triage.get("type_overrides", {}), triage.get("duplicates", {})
    _remove_previous(backlog, profile)

    dup_notes, type_notes, wontdo, drafts, draft_number = [], [], [], [], 0
    for issue in issues:
        folder = _placement(issue, triage, duplicated)
        upstream_cr = _triage_entry(upstream, issue, duplicated)
        cr_type = (dup_types.get(issue.rel_path) or _triage_entry(overrides, issue, duplicated)
                   or TYPE_MAP[issue.type])
        if cr_type != issue.type:
            type_notes.append(f"#{issue.number:03d}: {issue.type!r} -> {cr_type}")
        labels, final_summary, status, project = [], None, "To Do", profile.project
        if upstream_cr:
            task_id, status, labels, project = f"CR-{ids[issue.rel_path]}", "Done", ["wontdo"], UPSTREAM
            final_summary = f"Duplicate of CR-{upstream_cr}, filed upstream by hand."
            dup_notes.append(f"#{issue.number:03d} -> {task_id}: duplicate of CR-{upstream_cr}")
        elif folder == "completed":
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
        description = f"{body}\n\n{profile.provenance_prefix}{issue.number:03d}."
        text = render_task(task_id=task_id, title=issue.title, status=status, created=issue.date,
                           labels=labels, description=description, type_=cr_type,
                           project=project, final_summary=final_summary)
        (backlog / folder / filename_for(task_id, issue.title)).write_text(text, encoding="utf-8")

    counts = expected_counts(issues, triage)
    sections = [
        ("Duplicates of plcc-ng issues", dup_notes),
        ("Duplicate-number remaps", remaps),
        ("Type mappings (non-identity)", type_notes),
        ("Won't-do (abandoned or superseded)", wontdo),
        ("Drafts (lose their number; provenance line keeps it greppable)", drafts),
        ("Link findings", ctx.findings),
    ]
    lines = [f"# {profile.project} migration report", "",
             f"Converted {len(issues)} files: {counts['completed']} -> completed/, "
             f"{counts['tasks']} -> tasks/, {counts['drafts']} -> drafts/.", ""]
    for title, items in sections:
        lines += [f"## {title}", ""] + ([f"- {item}" for item in items] or ["(none)"]) + [""]
    return "\n".join(lines)


def main(argv=None, profile=PLCC_NG, doc=__doc__):
    parser = argparse.ArgumentParser(description=doc.splitlines()[0])
    parser.add_argument("--repo", required=True, type=Path)
    parser.add_argument("--tracker", required=True, type=Path)
    parser.add_argument("--triage", required=True, type=Path)
    parser.add_argument("--report", required=True, type=Path)
    args = parser.parse_args(argv)
    triage = json.loads(args.triage.read_text(encoding="utf-8"))
    report = convert(args.repo, args.tracker, triage, profile)
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(report, encoding="utf-8")
    print(report.splitlines()[2])
    return 0


if __name__ == "__main__":
    sys.exit(main())
