import io
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

from migrate import split_links

TASK = """\
---
id: CR-1
title: A
references:
  - ../../dev-docs/specs/s.md
  - ../../../plcc-ng/dev-docs/specs/p.md
  - https://github.com/ourPLCC/plcc-ng/issues/1
type: chore
project: dev
---

## Description

See [verify](../../migrate/verify.py#L10), [emit](../../../plcc-ng/emit.py),
[doc](../../backlog/docs/d.md), and [`TEMPLATE.md`](../../TEMPLATE.md).
"""


class SplitLinksTest(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        base = Path(self._tmp.name)
        self.dev = base / "dev"
        (self.dev / "dev-docs" / "specs").mkdir(parents=True)
        (self.dev / "dev-docs" / "specs" / "s.md").write_text("spec\n")
        (self.dev / "migrate").mkdir()
        (self.dev / "migrate" / "verify.py").write_text("")
        (self.dev / "backlog" / "docs").mkdir(parents=True)
        (self.dev / "backlog" / "docs" / "d.md").write_text("")
        self.tracker = base / "split"
        (self.tracker / "backlog" / "tasks").mkdir(parents=True)
        self.task = self.tracker / "backlog" / "tasks" / "cr-1 - A.md"
        self.task.write_text(TASK)
        self.outside = self.tracker / "README.md"
        self.outside.write_text("[x](../../migrate/verify.py)\n")

    def tearDown(self):
        self._tmp.cleanup()

    def test_target_into_dev_is_rewritten(self):
        self.assertEqual(split_links.rewrite_target("../../dev-docs/specs/s.md", self.dev),
                         "../../../dev/dev-docs/specs/s.md")

    def test_fragment_is_kept_and_ignored_for_existence(self):
        self.assertEqual(split_links.rewrite_target("../../migrate/verify.py#L10", self.dev),
                         "../../../dev/migrate/verify.py#L10")

    def test_sibling_repo_target_is_left_alone(self):
        self.assertIsNone(split_links.rewrite_target("../../../plcc-ng/emit.py", self.dev))

    def test_target_inside_backlog_is_left_alone(self):
        self.assertIsNone(split_links.rewrite_target("../../backlog/docs/d.md", self.dev))

    def test_missing_target_is_left_alone(self):
        self.assertIsNone(split_links.rewrite_target("../../TEMPLATE.md", self.dev))

    def test_url_is_left_alone(self):
        self.assertIsNone(split_links.rewrite_target("https://github.com/ourPLCC/dev", self.dev))

    def test_rewrite_tracker(self):
        changes, skipped = split_links.rewrite_tracker(self.tracker, self.dev)
        text = self.task.read_text()
        self.assertIn("  - ../../../dev/dev-docs/specs/s.md\n", text)
        self.assertIn("[verify](../../../dev/migrate/verify.py#L10)", text)
        self.assertIn("  - ../../../plcc-ng/dev-docs/specs/p.md\n", text)
        self.assertIn("[emit](../../../plcc-ng/emit.py)", text)
        self.assertIn("[doc](../../backlog/docs/d.md)", text)
        self.assertIn("(../../TEMPLATE.md)", text)
        rel = "backlog/tasks/cr-1 - A.md"
        self.assertEqual(changes, [
            (rel, "../../dev-docs/specs/s.md", "../../../dev/dev-docs/specs/s.md"),
            (rel, "../../migrate/verify.py#L10", "../../../dev/migrate/verify.py#L10"),
        ])
        self.assertEqual(skipped, [(rel, "../../backlog/docs/d.md"), (rel, "../../TEMPLATE.md")])

    def test_files_outside_backlog_are_untouched(self):
        split_links.rewrite_tracker(self.tracker, self.dev)
        self.assertEqual(self.outside.read_text(), "[x](../../migrate/verify.py)\n")

    def test_check_mode_writes_nothing(self):
        changes, _ = split_links.rewrite_tracker(self.tracker, self.dev, write=False)
        self.assertEqual(len(changes), 2)
        self.assertEqual(self.task.read_text(), TASK)

    def test_cli_check_reports_and_exits_1(self):
        out = io.StringIO()
        with redirect_stdout(out):
            code = split_links.main(["--tracker", str(self.tracker), "--dev", str(self.dev), "--check"])
        self.assertEqual(code, 1)
        self.assertIn("would change: backlog/tasks/cr-1 - A.md: ../../dev-docs/specs/s.md -> "
                      "../../../dev/dev-docs/specs/s.md", out.getvalue())
        self.assertIn("skipped: backlog/tasks/cr-1 - A.md: ../../TEMPLATE.md", out.getvalue())
        self.assertIn("split_links: 2 changed, 2 skipped", out.getvalue())
        self.assertEqual(self.task.read_text(), TASK)

    def test_cli_write_exits_0(self):
        with redirect_stdout(io.StringIO()):
            code = split_links.main(["--tracker", str(self.tracker), "--dev", str(self.dev)])
        self.assertEqual(code, 0)
        self.assertIn("../../../dev/dev-docs/specs/s.md", self.task.read_text())


if __name__ == "__main__":
    unittest.main()
