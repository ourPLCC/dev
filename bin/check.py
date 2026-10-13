#!/usr/bin/env python3
"""Consistency checks for the ourPLCC change-request tracker.

Standard library only: this runs from the hooks and in CI without Node or
Backlog.md. --root names the tracker repo (ourPLCC/change-requests).
"""
import argparse
import re
import subprocess
import sys
from pathlib import Path

SEED_ID = "CR-999"
RECORD_FOLDERS = ("tasks", "completed", "drafts", "archive/tasks")
CR_FOLDERS = ("tasks", "completed")
ID_FILENAME_RE = re.compile(r"^(cr|draft)-(\d+(?:\.\d+)*) - ", re.IGNORECASE)
DRAFT_REF_RE = re.compile(r"\bDRAFT-(\d+)\b")
KEY_RE = re.compile(r"^([A-Za-z_][\w-]*):(.*)$")


def _scalar(value):
    value = value.strip()
    if len(value) >= 2 and value[0] == value[-1] == "'":
        return value[1:-1].replace("''", "'")
    if len(value) >= 2 and value[0] == value[-1] == '"':
        return value[1:-1]
    return value


def _parse_block(lines):
    """Parse the YAML subset Backlog.md writes: scalars, [a, b], '- item' lists."""
    data, key = {}, None
    for line in lines:
        if line.startswith("  - ") and key is not None:
            if not isinstance(data.get(key), list):
                data[key] = []
            data[key].append(_scalar(line[4:]))
            continue
        m = KEY_RE.match(line)
        if not m:
            continue
        key, value = m.group(1), m.group(2).strip()
        if value.startswith("[") and value.endswith("]"):
            inner = value[1:-1].strip()
            data[key] = [_scalar(v) for v in inner.split(",")] if inner else []
        elif value == "":
            data[key] = []
        else:
            data[key] = _scalar(value)
    return data


def parse_frontmatter(text):
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return {}
    end = next((i for i, line in enumerate(lines[1:], 1) if line.strip() == "---"), len(lines))
    return _parse_block(lines[1:end])


def load_config(path):
    return _parse_block(Path(path).read_text(encoding="utf-8").splitlines())


def _as_list(value):
    if value is None:
        return []
    return [value] if isinstance(value, str) else list(value)


def check(root, pre_push=False):
    root = Path(root)
    backlog = root / "backlog"
    config = load_config(backlog / "config.yml")
    projects = _as_list(config.get("projects"))
    types = _as_list(config.get("types"))
    labels = _as_list(config.get("labels"))
    errors = []

    def rel(path):
        return path.relative_to(root).as_posix()

    for path in sorted((backlog / "archive").rglob("*.md")):
        errors.append(f"{rel(path)}: archived file; we never archive (use Done + wontdo)")

    records = []
    for folder in RECORD_FOLDERS:
        for path in sorted((backlog / folder).glob("*.md")):
            records.append((folder, path, parse_frontmatter(path.read_text(encoding="utf-8"))))

    seen = {}
    for folder, path, fm in records:
        fid = str(fm.get("id", ""))
        m = ID_FILENAME_RE.match(path.name)
        if not m or f"{m.group(1)}-{m.group(2)}".upper() != fid.upper():
            errors.append(f"{rel(path)}: filename does not match id {fid!r}")
        if fid:
            key = fid.upper()
            if key in seen:
                errors.append(f"{rel(path)}: duplicate id {key} (also {seen[key]})")
            else:
                seen[key] = rel(path)

    for path in sorted(backlog.rglob("*.md")):
        text = path.read_text(encoding="utf-8")
        own = str(parse_frontmatter(text).get("id", "")).upper()
        for n in sorted(set(DRAFT_REF_RE.findall(text)), key=int):
            if f"DRAFT-{n}" != own:
                errors.append(f"{rel(path)}: cites DRAFT-{n}; drafts are never cited")

    for folder, path, fm in records:
        fid = str(fm.get("id", "")).upper()
        if folder in CR_FOLDERS and fid != SEED_ID:
            project = fm.get("project")
            if not isinstance(project, str) or project not in projects:
                errors.append(f"{rel(path)}: project {project!r} is not exactly one of {projects}")
            ctype = fm.get("type")
            if not isinstance(ctype, str) or ctype not in types:
                errors.append(f"{rel(path)}: type {ctype!r} is not one of {types}")
        for label in _as_list(fm.get("labels")):
            if label not in labels:
                errors.append(f"{rel(path)}: label {label!r} is not one of {labels}")

    if pre_push:
        out = subprocess.run(
            ["git", "-C", str(root), "status", "--porcelain", "--untracked-files=all", "--", "backlog"],
            capture_output=True, text=True, check=True).stdout
        for line in out.splitlines():
            errors.append(f"uncommitted change under backlog/: {line}")
    return errors


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--root", required=True,
                        help="root of the tracker repo, which holds backlog/")
    parser.add_argument("--pre-push", action="store_true",
                        help="also fail on uncommitted changes under backlog/")
    args = parser.parse_args(argv)
    errors = check(args.root, pre_push=args.pre_push)
    for error in errors:
        print(f"check: {error}", file=sys.stderr)
    if errors:
        return 1
    print("check: ok")
    return 0


if __name__ == "__main__":
    sys.exit(main())
