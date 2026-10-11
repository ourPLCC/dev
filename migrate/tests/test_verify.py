import contextlib
import io
import json
import os
import re
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from migrate import languages_ng, plcc_ng, verify
from migrate.emit import render_task

TRACKER = Path(__file__).resolve().parents[2]
HAS_BACKLOG = shutil.which("backlog") is not None


@unittest.skipUnless(HAS_BACKLOG, "backlog CLI not installed")
class VerifyTest(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        base = Path(self._tmp.name)
        self.repo, self.tracker = base / "plcc-ng", base / "issues"
        issues = self.repo / "dev-docs" / "issues"
        (issues / "done").mkdir(parents=True)
        (issues / "done" / "010-old.md").write_text("# 010 - Old: thing\n\n**Type:** bug\n**Date:** 2026-01-01\n\n## Description\n\nO.\n")
        (issues / "160-race.md").write_text("# 160 - Race\n\n**Type:** fix\n**Date:** 2026-07-01\n\n## Description\n\nR.\n")
        (issues / "170-idea.md").write_text("# 170 - Idea\n\n**Type:** feat\n**Date:** 2026-07-02\n\n## Description\n\nI.\n")
        self.tracker.mkdir()
        for name in ("backlog", "bin"):
            shutil.copytree(TRACKER / name, self.tracker / name,
                            ignore=shutil.ignore_patterns("tasks", "completed", "drafts", "archive"))
        for folder in ("tasks", "completed", "drafts"):
            (self.tracker / "backlog" / folder).mkdir(exist_ok=True)
        shutil.copy(TRACKER / "backlog" / "completed" / "cr-999 - Tracker-begins-here.md",
                    self.tracker / "backlog" / "completed")
        cfg = self.tracker / "backlog" / "config.yml"
        cfg.write_text(cfg.read_text().replace("auto_commit: true", "auto_commit: false")
                       .replace("remote_operations: true", "remote_operations: false"))
        subprocess.run(["git", "init", "-q", str(self.tracker)], check=True)
        subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@t", "-C", str(self.tracker),
                        "commit", "-q", "--allow-empty", "-m", "init"], check=True)
        self.triage = {"open": {"160": {"as": "cr", "status": "To Do", "reason": "r"},
                                "170": {"as": "draft", "reason": "r"}}}
        plcc_ng.convert(self.repo, self.tracker, self.triage)

    def tearDown(self):
        self._tmp.cleanup()

    def test_verify_passes_on_converted_tracker(self):
        self.assertEqual(verify.verify(self.repo, self.tracker, self.triage), [])

    def test_verify_detects_missing_file(self):
        next((self.tracker / "backlog" / "completed").glob("cr-10 *")).unlink()
        self.assertTrue(any("completed" in e for e in verify.verify(self.repo, self.tracker, self.triage)))

    def _drop_id(self, folder, prefix):
        path = next((self.tracker / "backlog" / folder).glob(f"{prefix} *"))
        path.write_text(re.sub(r"^id: .*\n", "", path.read_text(), count=1, flags=re.MULTILINE))
        return f"{folder}/{path.name}"

    def test_verify_reports_files_without_id(self):
        task = self._drop_id("tasks", "cr-160")
        draft = self._drop_id("drafts", "draft-1")
        errors = verify.verify(self.repo, self.tracker, self.triage)
        self.assertIn(f"{task}: no id: line in frontmatter", errors)
        self.assertIn(f"{draft}: no id: line in frontmatter", errors)

    def test_verify_ignores_id_line_outside_frontmatter(self):
        task = self._drop_id("tasks", "cr-160")
        path = self.tracker / "backlog" / task
        path.write_text(path.read_text() + "\nid: CR-160\n")
        errors = verify.verify(self.repo, self.tracker, self.triage)
        self.assertIn(f"{task}: no id: line in frontmatter", errors)

    def test_main_exits_nonzero_on_missing_id(self):
        task = self._drop_id("tasks", "cr-160")
        triage = Path(self._tmp.name) / "triage.json"
        triage.write_text(json.dumps(self.triage))
        stderr = io.StringIO()
        with contextlib.redirect_stderr(stderr):
            status = verify.main(["--repo", str(self.repo), "--tracker", str(self.tracker),
                                  "--triage", str(triage)])
        self.assertEqual(status, 1)
        self.assertIn(f"{task}: no id: line in frontmatter", stderr.getvalue())

    def test_verify_ignores_cr_that_quotes_provenance_line(self):
        description = "Migrated from plcc-ng #160.\n\nCR-160 ends with that line."
        (self.tracker / "backlog" / "tasks" / "cr-1000 - Quote.md").write_text(
            render_task(task_id="CR-1000", title="Quote", status="To Do", created="2026-10-10",
                        labels=[], description=description, type_="chore", project="dev"))
        self.assertEqual(verify.verify(self.repo, self.tracker, self.triage), [])

    def test_verify_ignores_ambient_backlog_cwd(self):
        decoy = Path(self._tmp.name) / "decoy"
        decoy.mkdir()
        with mock.patch.dict(os.environ, {"BACKLOG_CWD": str(decoy)}):
            self.assertEqual(verify.verify(self.repo, self.tracker, self.triage), [])


@unittest.skipUnless(HAS_BACKLOG, "backlog CLI not installed")
class LanguagesNgVerifyTest(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        base = Path(self._tmp.name)
        self.repo, self.tracker = base / "languages-ng", base / "tracker"
        issues = self.repo / "dev-docs" / "issues"
        issues.mkdir(parents=True)
        front = "---\ntype: {}\ntarget: this repo\nopened: 2026-07-22\nclosed: {}\n---\n\n"
        (issues / "012-ci.md").write_text(front.format("chore", "2026-08-01") +
                                          "# 012 - CI\n\n## Description\n\nC.\n")
        (issues / "031-disk.md").write_text(front.format("test", "") +
                                            "# 031 - Disk\n\n## Description\n\nUnlike #187.\n")
        self.tracker.mkdir()
        for name in ("backlog", "bin"):
            shutil.copytree(TRACKER / name, self.tracker / name,
                            ignore=shutil.ignore_patterns("tasks", "completed", "drafts", "archive"))
        for folder in ("tasks", "completed", "drafts"):
            (self.tracker / "backlog" / folder).mkdir(exist_ok=True)
        shutil.copy(TRACKER / "backlog" / "completed" / "cr-999 - Tracker-begins-here.md",
                    self.tracker / "backlog" / "completed")
        cfg = self.tracker / "backlog" / "config.yml"
        cfg.write_text(cfg.read_text().replace("auto_commit: true", "auto_commit: false")
                       .replace("remote_operations: true", "remote_operations: false"))
        subprocess.run(["git", "init", "-q", str(self.tracker)], check=True)
        subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@t", "-C", str(self.tracker),
                        "commit", "-q", "--allow-empty", "-m", "init"], check=True)
        self.triage = {"open": {"31": {"as": "cr", "reason": "r"}}}

    def tearDown(self):
        self._tmp.cleanup()

    def test_unresolved_reference_fails_verify_until_decided(self):
        languages_ng.convert(self.repo, self.tracker, self.triage)
        self.assertEqual(verify.verify(self.repo, self.tracker, self.triage, languages_ng),
                         ['unresolved reference, add a triage entry: 31: #187 in "Unlike #187."'])
        self.triage["references"] = {"31": {"#187": "CR-187"}}
        languages_ng.convert(self.repo, self.tracker, self.triage)
        self.assertEqual(verify.verify(self.repo, self.tracker, self.triage, languages_ng), [])

    def test_main_takes_driver(self):
        self.triage["references"] = {"31": {"#187": "CR-187"}}
        languages_ng.convert(self.repo, self.tracker, self.triage)
        triage = Path(self._tmp.name) / "triage.json"
        triage.write_text(json.dumps(self.triage))
        status = verify.main(["--repo", str(self.repo), "--tracker", str(self.tracker),
                              "--triage", str(triage), "--driver", "languages-ng"])
        self.assertEqual(status, 0)


if __name__ == "__main__":
    unittest.main()
