"""Count citations of each open legacy issue, as triage evidence.

Usage: python3 -m migrate.citations --repo REPO [--driver plcc-ng|languages-ng]
"""
import argparse
import re
import subprocess
import sys
from pathlib import Path

from migrate import drivers

COMMIT_SEP = "\x1eEND\x1e"


def cite_pattern(number):
    n = rf"0*{number}"
    return re.compile(
        rf"(?<![\w/&#])#{n}\b|\bissues?\s+#?{n}\b|(?<![\w-])(?:issues/(?:done/)?)?{n}-[a-z][\w-]*\.md")


def _git_messages(repo_root):
    out = subprocess.run(
        ["git", "-c", f"safe.directory={repo_root}", "-C", str(repo_root), "log",
         f"--format=%s%n%b{COMMIT_SEP}"],
        capture_output=True, text=True, check=True).stdout
    return [m.strip() for m in out.split(COMMIT_SEP) if m.strip()]


def count_citations(repo_root, number, own_paths, _messages=None):
    repo_root = Path(repo_root)
    pattern = cite_pattern(number)
    issue_files = [p for p in (repo_root / "dev-docs/issues").rglob("[0-9]*.md")
                   if p.relative_to(repo_root).as_posix() not in own_paths]
    doc_files = [p for d in ("dev-docs/specs", "dev-docs/plans") for p in (repo_root / d).rglob("*.md")]
    messages = _messages if _messages is not None else _git_messages(repo_root)
    return {
        "issues": sum(1 for p in issue_files if pattern.search(p.read_text(encoding="utf-8"))),
        "docs": sum(1 for p in doc_files if pattern.search(p.read_text(encoding="utf-8"))),
        "commits": sum(1 for m in messages
                       if not m.startswith("docs(issues):") and pattern.search(m)),
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--repo", required=True, type=Path)
    parser.add_argument("--driver", choices=sorted(drivers.DRIVERS), default="plcc-ng")
    args = parser.parse_args(argv)
    issues = drivers.load(args.driver).load_issues(args.repo)
    messages = _git_messages(args.repo)
    for issue in (i for i in issues if not i.closed):
        same = {i.rel_path for i in issues if i.number == issue.number}
        c = count_citations(args.repo, issue.number, same, messages)
        print(f"#{issue.number:03d} issues={c['issues']} docs={c['docs']} commits={c['commits']}  {issue.title}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
