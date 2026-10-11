import json
import tempfile
import textwrap
import unittest
from pathlib import Path

from migrate import languages_ng
from migrate.emit import render_task

OBSOLETE = "Obsolete: languages-ng's file-based tracker was retired."


def issue(number, title, type_="fix", target="this repo", closed="2026-08-01", body="Body.", summary=""):
    summary_section = f"## Summary\n\n{summary}\n\n" if summary else ""
    return textwrap.dedent(f"""\
        ---
        type: {type_}
        target: {target}
        opened: 2026-07-22
        closed: {closed}
        ---

        # {number:03d} - {title}

        """) + summary_section + f"## Description\n\n{body}\n\n## Notes\n\nN.\n"


class LanguagesNgTestCase(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        base = Path(self._tmp.name)
        self.repo, self.tracker = base / "languages-ng", base / "tracker"
        self.issues = self.repo / "dev-docs" / "issues"
        self.issues.mkdir(parents=True)
        files = {
            "003-python-quoted.md": issue(3, "Python quoted", "docs", "ourPLCC/plcc-ng"),
            "012-ci.md": issue(12, "CI", "chore", body="Merged in PR #12; see #31."),
            "031-disk.md": issue(31, "Disk", "test", closed="", summary="Disk fills.",
                                 body="Unlike #187, see [#12](012-ci.md)."),
            "037-records.md": issue(37, "Records", "chore", "ourPLCC/plcc-ng", closed=""),
            "042-slow.md": issue(42, "Slow", "chore", closed=""),
            "043-help.md": issue(43, "Help", "chore", closed=""),
            "TEMPLATE.md": "---\ntype: TYPE\n---\n# NNN - Short title\n",
            "index.md": "# Issues\n",
        }
        for name, text in files.items():
            (self.issues / name).write_text(text)
        self.backlog = self.tracker / "backlog"
        for folder in ("tasks", "completed", "drafts"):
            (self.backlog / folder).mkdir(parents=True)
        self.write_cr("completed", 162, "Python quoted upstream", "docs", "Done")
        self.write_cr("tasks", 187, "Records upstream", "feat", "To Do")
        self.triage = {
            "open": {"31": {"as": "cr", "status": "In Progress", "reason": "r"},
                     "42": {"as": "draft", "reason": "r"},
                     "43": {"as": "wontdo", "summary": OBSOLETE, "reason": "r"}},
            "duplicates": {"3": 162, "37": 187},
            "references": {"31": {"#187": "CR-187"}},
        }

    def tearDown(self):
        self._tmp.cleanup()

    def write_cr(self, folder, cr, title, type_, status):
        description = f"Upstream.\n\nMigrated from plcc-ng #{cr:03d}."
        (self.backlog / folder / f"cr-{cr} - {title.replace(' ', '-')}.md").write_text(
            render_task(task_id=f"CR-{cr}", title=title, status=status, created="2026-07-28",
                        labels=[], description=description, type_=type_, project="plcc-ng"))

    def load(self):
        return languages_ng.load_issues(self.repo)


class LoadAndValidateTest(LanguagesNgTestCase):
    def test_load_reads_numbered_files_only(self):
        self.assertEqual([i.number for i in self.load()], [3, 12, 31, 37, 42, 43])

    def test_issue_refs_use_offset_500(self):
        refs = languages_ng.issue_refs(self.load())
        self.assertEqual(refs[12][0].cr, 512)
        self.assertEqual(refs[12][0].slug, "ci")

    def test_expected_counts(self):
        self.assertEqual(languages_ng.expected_counts(self.load(), self.triage),
                         {"tasks": 1, "completed": 4, "drafts": 1})

    def test_tracker_type(self):
        self.assertEqual(languages_ng.tracker_type(self.backlog, 162), "docs")
        self.assertEqual(languages_ng.tracker_type(self.backlog, 187), "feat")
        self.assertIsNone(languages_ng.tracker_type(self.backlog, 999))

    def test_validate_returns_duplicate_types(self):
        self.assertEqual(languages_ng.validate(self.load(), self.triage, self.backlog),
                         {3: "docs", 37: "feat"})

    def assert_invalid(self, *fragments):
        with self.assertRaises(SystemExit) as cm:
            languages_ng.validate(self.load(), self.triage, self.backlog)
        for fragment in fragments:
            self.assertIn(fragment, str(cm.exception))

    def test_untriaged_open_issue(self):
        del self.triage["open"]["42"]
        self.assert_invalid("#042 is open but has no valid triage entry")

    def test_wontdo_needs_summary(self):
        del self.triage["open"]["43"]["summary"]
        self.assert_invalid("#043 is triaged wontdo but has no summary")

    def test_duplicate_of_missing_cr(self):
        self.triage["duplicates"]["37"] = 186
        self.assert_invalid("#037 duplicates CR-186")

    def test_unknown_target(self):
        (self.issues / "050-x.md").write_text(issue(50, "X", target="ourPLCC/plcc-ng-demo"))
        self.assert_invalid("#050 has target 'ourPLCC/plcc-ng-demo'")

    def test_unmapped_type(self):
        (self.issues / "050-x.md").write_text(issue(50, "X", type_="warning"))
        self.assert_invalid("#050 has type 'warning'")
        self.triage["type_overrides"] = {"50": "chore"}
        languages_ng.validate(self.load(), self.triage, self.backlog)

    def test_triage_key_that_is_not_an_issue(self):
        self.triage["references"]["99"] = {"#1": "CR-501"}
        self.assert_invalid("references key '99' is not a languages-ng issue number")

    def test_repeated_number(self):
        (self.issues / "012-ci-again.md").write_text(issue(12, "CI again"))
        self.assert_invalid("#012 is used by more than one file")


if __name__ == "__main__":
    unittest.main()
