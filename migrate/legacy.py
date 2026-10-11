"""Parse one issue file in a legacy dev-docs/issues/ format (plcc-ng's or languages-ng's)."""
import re
from dataclasses import dataclass
from pathlib import Path

from migrate.emit import demote_headings

TITLE_RE = re.compile(r"^# (\d+) - (.+?)\s*$")
FILE_RE = re.compile(r"^(\d+)-(.+)\.md$")
FIELD_RE = re.compile(r"^\*\*(Type|Date|Status):\*\*\s*(.*?)\s*$")
DATE_RE = re.compile(r"\d{4}-\d{2}-\d{2}")
TEMPLATE_COMMENT_RE = re.compile(r"<!--(?:(?!-->).)*Classify by user-facing impact.*?-->\n?", re.S)
FRONTMATTER_RE = re.compile(r"\A---\n(.*?)\n---\n", re.S)
FRONTMATTER_LINE_RE = re.compile(r"^([a-z_]+):[ \t]*(.*?)\s*$")
FRONTMATTER_REQUIRED = ("type", "target", "opened", "closed")
FRONTMATTER_OPTIONAL = ("upstream",)


@dataclass(frozen=True)
class LegacyIssue:
    number: int
    slug: str
    rel_path: str
    title: str
    type: str
    date: str
    status_note: str
    closed: bool
    preamble: str
    sections: tuple
    target: str = ""


def split_body(lines, read_fields=True):
    """Split body lines into (fields, preamble, sections); headings inside fences do not count."""
    fields, preamble, sections = {}, [], []
    heading, buf, in_fence = None, [], False
    for line in lines:
        if line.lstrip().startswith("```"):
            in_fence = not in_fence
        if not in_fence and line.startswith("## "):
            if heading is None:
                preamble = buf
            else:
                sections.append((heading, "\n".join(buf).strip("\n")))
            heading, buf = line[3:].strip(), []
            continue
        if read_fields and heading is None and not in_fence:
            field = FIELD_RE.match(line)
            if field:
                fields[field.group(1)] = field.group(2)
                continue
        buf.append(line)
    if heading is None:
        preamble = buf
    else:
        sections.append((heading, "\n".join(buf).strip("\n")))
    return fields, "\n".join(preamble).strip("\n"), tuple(sections)


def parse_issue(path, repo_root):
    path, repo_root = Path(path), Path(repo_root)
    text = TEMPLATE_COMMENT_RE.sub("", path.read_text(encoding="utf-8"), count=1)
    lines = text.splitlines()
    title_match = TITLE_RE.match(lines[0]) if lines else None
    file_match = FILE_RE.match(path.name)
    if not title_match or not file_match:
        raise ValueError(f"{path}: expected '# NNN - Title' and a NNN-slug.md filename")

    fields, preamble, sections = split_body(lines[1:])
    raw_type = fields.get("Type", "").split()
    date = DATE_RE.search(fields.get("Date", ""))
    return LegacyIssue(
        number=int(file_match.group(1)),
        slug=file_match.group(2),
        rel_path=path.relative_to(repo_root).as_posix(),
        title=title_match.group(2),
        type=raw_type[0].lower().strip("`,.:;") if raw_type else "",
        date=date.group(0) if date else "",
        status_note=fields.get("Status", ""),
        closed="done" in path.relative_to(repo_root).parts,
        preamble=preamble,
        sections=sections,
    )


def _read_frontmatter(path, text):
    match = FRONTMATTER_RE.match(text)
    if not match:
        raise ValueError(f"{path}: expected frontmatter between '---' lines")
    meta = {}
    for line in match.group(1).split("\n"):
        pair = FRONTMATTER_LINE_RE.match(line)
        if not pair:
            raise ValueError(f"{path}: unreadable frontmatter line {line!r}")
        meta[pair.group(1)] = pair.group(2)
    unknown = sorted(set(meta) - set(FRONTMATTER_REQUIRED) - set(FRONTMATTER_OPTIONAL))
    missing = [key for key in FRONTMATTER_REQUIRED if key not in meta]
    if unknown or missing:
        raise ValueError(f"{path}: frontmatter has unknown keys {unknown} and lacks {missing}")
    return meta, text[match.end():]


def parse_frontmatter_issue(path, repo_root):
    """Parse one issue in languages-ng's format: frontmatter, closure recorded in `closed:`."""
    path, repo_root = Path(path), Path(repo_root)
    meta, body = _read_frontmatter(path, path.read_text(encoding="utf-8"))
    lines = TEMPLATE_COMMENT_RE.sub("", body, count=1).lstrip("\n").splitlines()
    title_match = TITLE_RE.match(lines[0]) if lines else None
    file_match = FILE_RE.match(path.name)
    if not title_match or not file_match:
        raise ValueError(f"{path}: expected '# NNN - Title' and a NNN-slug.md filename")
    if int(title_match.group(1)) != int(file_match.group(1)):
        raise ValueError(f"{path}: title number {title_match.group(1)} does not match the filename")
    date = DATE_RE.fullmatch(meta["opened"])
    if not date:
        raise ValueError(f"{path}: opened: {meta['opened']!r} is not a YYYY-MM-DD date")
    _, preamble, sections = split_body(lines[1:], read_fields=False)
    summaries = [text for heading, text in sections if heading.lower() == "summary" and text.strip()]
    lead = [preamble] if preamble.strip() else []
    lead += [f"### Summary\n\n{demote_headings(summary.strip())}" for summary in summaries]
    if summaries:
        # Under a Summary, the description needs its own heading or it reads as part of the summary.
        lead += [f"### Description\n\n{text.strip()}" for heading, text in sections
                 if heading.lower() == "description" and text.strip()]
        sections = tuple((h, b) for h, b in sections if h.lower() != "description")
    return LegacyIssue(
        number=int(file_match.group(1)),
        slug=file_match.group(2),
        rel_path=path.relative_to(repo_root).as_posix(),
        title=title_match.group(2),
        type=meta["type"].lower(),
        date=date.group(0),
        status_note="",
        closed=bool(meta["closed"]),
        preamble="\n\n".join(lead),
        sections=tuple((h, b) for h, b in sections if h.lower() != "summary"),
        target=meta["target"],
    )
