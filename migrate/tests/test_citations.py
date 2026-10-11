import contextlib
import io
import subprocess
import tempfile
import unittest
from pathlib import Path

from migrate import citations
from migrate.citations import cite_pattern, count_citations


class CitationsTest(unittest.TestCase):
    def test_pattern(self):
        p = cite_pattern(61)
        for hit in ("see #61.", "#061 fixed", "issue 61 is", "issues/done/061-x.md", "(061-x.md)"):
            self.assertTrue(p.search(hit), hit)
        for miss in ("#610", "&#61;", "ourPLCC/plcc-ng#61", "2026-061-x"):
            self.assertFalse(p.search(miss), miss)

    def test_count(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            (repo / "dev-docs/issues").mkdir(parents=True)
            (repo / "dev-docs/specs").mkdir()
            (repo / "dev-docs/issues/061-a.md").write_text("# 061 - A\nself #61\n")
            (repo / "dev-docs/issues/062-b.md").write_text("# 062 - B\nsee #61\n")
            (repo / "dev-docs/specs/s.md").write_text("Issue: [#61](../issues/061-a.md)\n")
            git = ["git", "-c", "user.name=t", "-c", "user.email=t@t", "-C", tmp]
            subprocess.run(git + ["init", "-q"], check=True)
            subprocess.run(git + ["add", "-A"], check=True)
            subprocess.run(git + ["commit", "-q", "-m", "docs(issues): file 061 - a"], check=True)
            subprocess.run(git + ["commit", "-q", "--allow-empty", "-m", "fix: x (issue 61)"], check=True)
            counts = count_citations(repo, 61, {"dev-docs/issues/061-a.md"})
            self.assertEqual(counts, {"issues": 1, "docs": 1, "commits": 1})

    def test_main_takes_driver(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            (repo / "dev-docs/issues").mkdir(parents=True)
            (repo / "dev-docs/specs").mkdir()
            (repo / "dev-docs/issues/031-disk.md").write_text(
                "---\ntype: test\ntarget: this repo\nopened: 2026-08-06\nclosed:\n---\n\n"
                "# 031 - Disk\n\n## Description\n\nD.\n")
            (repo / "dev-docs/specs/s.md").write_text("Issue #31.\n")
            git = ["git", "-c", "user.name=t", "-c", "user.email=t@t", "-C", tmp]
            subprocess.run(git + ["init", "-q"], check=True)
            subprocess.run(git + ["add", "-A"], check=True)
            subprocess.run(git + ["commit", "-q", "-m", "docs(issues): file 031 - disk"], check=True)
            out = io.StringIO()
            with contextlib.redirect_stdout(out):
                citations.main(["--repo", tmp, "--driver", "languages-ng"])
            self.assertEqual(out.getvalue(), "#031 issues=0 docs=1 commits=0  Disk\n")


if __name__ == "__main__":
    unittest.main()
