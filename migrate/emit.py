"""Render Backlog.md task files from legacy issues."""
import re
from pathlib import Path

CORE_TYPES = ("fix", "feat", "docs", "test", "refactor", "chore")
TYPE_MAP = {"bug": "fix", "enhancement": "feat", "feature": "feat", "perf": "fix",
            **{t: t for t in CORE_TYPES}}
WONTDO_RE = re.compile(r"^(abandoned|superseded)\b", re.IGNORECASE)
HEADING_RE = re.compile(r"^#{1,5} ")
TYPE_LINE_RE = re.compile(r"^type: (\S+)$", re.MULTILINE)


def yaml_quote(s):
    return "'" + s.replace("'", "''") + "'"


def slugify(title):
    slug = re.sub(r"[^A-Za-z0-9]+", "-", title).strip("-")
    return slug[:80].rstrip("-") or "untitled"


def filename_for(task_id, title):
    return f"{task_id.lower()} - {slugify(title)}.md"


def demote_headings(md):
    out, fence = [], False
    for line in md.split("\n"):
        if line.lstrip().startswith("```"):
            fence = not fence
        elif not fence and HEADING_RE.match(line):
            line = "#" + line
        out.append(line)
    return "\n".join(out)


def assemble_description(issue):
    parts = []
    if issue.preamble.strip():
        parts.append(issue.preamble.strip())
    for heading, body in issue.sections:
        if heading.lower() == "description" and body.strip():
            parts.append(body.strip())
    for heading, body in issue.sections:
        if heading.lower() != "description":
            parts.append(f"### {heading}\n\n{demote_headings(body.strip())}".rstrip())
    return "\n\n".join(parts)


def _section(name, marker, body):
    return f"## {name}\n\n<!-- SECTION:{marker}:BEGIN -->\n{body}\n<!-- SECTION:{marker}:END -->\n"


def render_task(*, task_id, title, status, created, labels, description,
                type_=None, project=None, final_summary=None):
    lines = ["---", f"id: {task_id}", f"title: {yaml_quote(title)}", f"status: {status}",
             "assignee: []", f"created_date: {yaml_quote(created)}"]
    if labels:
        lines.append("labels:")
        lines += [f"  - {label}" for label in labels]
    else:
        lines.append("labels: []")
    lines.append("dependencies: []")
    if type_ is not None:
        lines.append(f"type: {type_}")
    if project is not None:
        lines.append(f"project: {project}")
    lines += ["---", ""]
    text = "\n".join(lines) + "\n" + _section("Description", "DESCRIPTION", description.strip())
    if final_summary:
        text += "\n" + _section("Final Summary", "FINAL_SUMMARY", final_summary.strip())
    return text


def tracker_type(backlog, cr):
    """The type of CR-<cr> in the tracker, or None if the tracker has no such CR."""
    for folder in ("tasks", "completed"):
        for path in (Path(backlog) / folder).glob(f"cr-{cr} - *.md"):
            found = TYPE_LINE_RE.search(path.read_text(encoding="utf-8"))
            return found.group(1) if found else None
    return None
