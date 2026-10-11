"""Rewrite links into a code repo's retired dev-docs/issues/ tracker to CR IDs.

Usage: python3 -m migrate.repo_links --repo PATH --project plcc-ng|languages-ng [--check]
"""
import argparse
import posixpath
import sys
from pathlib import Path

from migrate import drivers
from migrate.links import LinkContext, rewrite_repo_doc

EXCLUDED_TOP_LEVEL = {"CHANGELOG.md"}


def target_files(repo_root):
    repo_root = Path(repo_root)
    files = [p for p in sorted(repo_root.glob("*.md")) if p.name not in EXCLUDED_TOP_LEVEL]
    files += [p for p in sorted((repo_root / "dev-docs").rglob("*.md"))
              if not p.relative_to(repo_root).as_posix().startswith("dev-docs/issues/")]
    files += sorted((repo_root / "docs").rglob("*.md"))
    return files


def rewrite_repo(repo_root, project, write=True):
    repo_root = Path(repo_root)
    driver = drivers.load(project)
    ctx = LinkContext(project, repo_root, driver.issue_refs(driver.load_issues(repo_root)), {}, "")
    changed = []
    for path in target_files(repo_root):
        rel = path.relative_to(repo_root).as_posix()
        text = path.read_text(encoding="utf-8")
        before = len(ctx.findings)
        new = rewrite_repo_doc(text, posixpath.dirname(rel), ctx)
        ctx.findings[before:] = [f"{rel}: {f}" for f in ctx.findings[before:]]
        if new != text:
            changed.append(rel)
            if write:
                path.write_text(new, encoding="utf-8")
    return changed, ctx.findings


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--repo", required=True, type=Path)
    parser.add_argument("--project", required=True, choices=sorted(drivers.DRIVERS))
    parser.add_argument("--check", action="store_true", help="report only; write nothing")
    args = parser.parse_args(argv)
    changed, findings = rewrite_repo(args.repo, args.project, write=not args.check)
    for rel in changed:
        print(f"{'would change' if args.check else 'changed'}: {rel}")
    for finding in findings:
        print(f"finding: {finding}")
    return 1 if (args.check and changed) else 0


if __name__ == "__main__":
    sys.exit(main())
