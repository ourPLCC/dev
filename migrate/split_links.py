"""Rewrite tracker references that pointed into dev, for the change-requests split.

Usage: python3 -m migrate.split_links --tracker PATH --dev PATH [--check]

Targets are resolved as if the file is in backlog/tasks/, where ../../X was
dev's root. After the split that is change-requests' root, so a target that
exists in dev outside backlog/ becomes ../../../dev/X. Everything else is left
alone. Only files under --tracker's backlog/ are read or written.
"""
import argparse
import re
import sys
from pathlib import Path

PREFIX = "../../"
NEW_PREFIX = "../../../dev/"
LINK_RE = re.compile(r"(\]\()(\.\./\.\./[^)\s]+)(\))")
REF_RE = re.compile(r"^(  - )(\.\./\.\./\S+)$", re.MULTILINE)


def rewrite_target(target, dev_root):
    if not target.startswith(PREFIX) or target.startswith(PREFIX + "../"):
        return None
    rest = target[len(PREFIX):]
    path = rest.split("#", 1)[0]
    if not path or path == "backlog" or path.startswith("backlog/"):
        return None
    if not (Path(dev_root) / path).exists():
        return None
    return NEW_PREFIX + rest


def _split_frontmatter(text):
    if text.startswith("---\n"):
        end = text.find("\n---\n", 4)
        if end != -1:
            return text[:end + 5], text[end + 5:]
    return "", text


def rewrite_text(text, dev_root):
    changes, skipped = [], []

    def sub(match):
        old = match.group(2)
        new = rewrite_target(old, dev_root)
        if new is None:
            if not old.startswith(PREFIX + "../"):
                skipped.append(old)
            return match.group(0)
        changes.append((old, new))
        return match.group(1) + new + match.group(0)[len(match.group(1)) + len(old):]

    front, body = _split_frontmatter(text)
    front = REF_RE.sub(sub, front)
    body = LINK_RE.sub(sub, body)
    return front + body, changes, skipped


def rewrite_tracker(tracker_root, dev_root, write=True):
    tracker_root = Path(tracker_root)
    all_changes, all_skipped = [], []
    for path in sorted((tracker_root / "backlog").rglob("*.md")):
        rel = path.relative_to(tracker_root).as_posix()
        text = path.read_text(encoding="utf-8")
        new, changes, skipped = rewrite_text(text, dev_root)
        all_changes += [(rel, old, repl) for old, repl in changes]
        all_skipped += [(rel, target) for target in skipped]
        if write and new != text:
            path.write_text(new, encoding="utf-8")
    return all_changes, all_skipped


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--tracker", required=True, type=Path,
                        help="root of the repo whose backlog/ is rewritten")
    parser.add_argument("--dev", required=True, type=Path,
                        help="root of a dev checkout, to test that targets exist")
    parser.add_argument("--check", action="store_true", help="report only; write nothing")
    args = parser.parse_args(argv)
    changes, skipped = rewrite_tracker(args.tracker, args.dev, write=not args.check)
    verb = "would change" if args.check else "changed"
    for rel, old, new in changes:
        print(f"{verb}: {rel}: {old} -> {new}")
    for rel, target in skipped:
        print(f"skipped: {rel}: {target}")
    print(f"split_links: {len(changes)} changed, {len(skipped)} skipped")
    return 1 if (args.check and changes) else 0


if __name__ == "__main__":
    sys.exit(main())
