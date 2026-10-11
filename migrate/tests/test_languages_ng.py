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


class ConvertTest(LanguagesNgTestCase):
    def files(self, folder):
        return sorted(p.name for p in (self.backlog / folder).glob("*.md"))

    def read(self, folder, name):
        return (self.backlog / folder / name).read_text()

    def test_convert_places_files(self):
        languages_ng.convert(self.repo, self.tracker, self.triage)
        self.assertEqual(self.files("completed"),
                         ["cr-162 - Python-quoted-upstream.md", "cr-503 - Python-quoted.md",
                          "cr-512 - CI.md", "cr-537 - Records.md", "cr-543 - Help.md"])
        self.assertEqual(self.files("tasks"), ["cr-187 - Records-upstream.md", "cr-531 - Disk.md"])
        self.assertEqual(self.files("drafts"), ["draft-1 - Slow.md"])

    def test_duplicates_are_wontdo_with_the_plcc_ng_type(self):
        languages_ng.convert(self.repo, self.tracker, self.triage)
        quoted = self.read("completed", "cr-503 - Python-quoted.md")
        for expected in ("status: Done", "  - wontdo", "type: docs", "project: plcc-ng",
                         "Duplicate of CR-162, filed upstream by hand."):
            self.assertIn(expected, quoted)
        records = self.read("completed", "cr-537 - Records.md")
        self.assertIn("type: feat", records)
        self.assertIn("Duplicate of CR-187, filed upstream by hand.", records)

    def test_open_issue_outcomes(self):
        languages_ng.convert(self.repo, self.tracker, self.triage)
        disk = self.read("tasks", "cr-531 - Disk.md")
        self.assertIn("status: In Progress", disk)
        self.assertIn("project: languages-ng", disk)
        self.assertIn("### Summary\n\nDisk fills.\n\nUnlike CR-187, see CR-512.", disk)
        self.assertIn("Migrated from languages-ng #031.\n<!-- SECTION:DESCRIPTION:END -->", disk)
        help_ = self.read("completed", "cr-543 - Help.md")
        self.assertIn("  - wontdo", help_)
        self.assertIn(OBSOLETE, help_)

    def test_references_in_body(self):
        languages_ng.convert(self.repo, self.tracker, self.triage)
        ci = self.read("completed", "cr-512 - CI.md")
        self.assertIn("Merged in PR [#12](https://github.com/ourPLCC/languages-ng/pull/12); "
                      "see CR-531.", ci)

    def test_report(self):
        report = languages_ng.convert(self.repo, self.tracker, self.triage)
        self.assertIn("Converted 6 files: 4 -> completed/, 1 -> tasks/, 1 -> drafts/.", report)
        self.assertIn("- #003 -> CR-503: duplicate of CR-162", report)
        self.assertIn("- 12: #31 -> CR-531", report)
        self.assertIn(f"- #043 -> CR-543: {OBSOLETE}", report)

    def test_unresolved_reference_is_reported(self):
        (self.issues / "044-git.md").write_text(issue(44, "Git", "test", closed="",
                                                      body="Same workaround as #186."))
        self.triage["open"]["44"] = {"as": "cr", "reason": "r"}
        # The context runs 30 characters past the reference, into the demoted Notes section.
        expected = ['44: #186 in "Same workaround as #186. ### Notes N."']
        self.assertEqual(languages_ng.unresolved_references(self.repo, self.triage), expected)
        report = languages_ng.convert(self.repo, self.tracker, self.triage)
        self.assertIn(f"- {expected[0]}", report)
        self.assertIn("Same workaround as #186.", self.read("tasks", "cr-544 - Git.md"))
        self.triage["references"]["44"] = {"#186": "CR-186"}
        self.assertEqual(languages_ng.unresolved_references(self.repo, self.triage), [])

    def test_rerun_replaces_only_its_own_output(self):
        languages_ng.convert(self.repo, self.tracker, self.triage)
        (self.issues / "042-slow.md").unlink()
        del self.triage["open"]["42"]
        languages_ng.convert(self.repo, self.tracker, self.triage)
        self.assertEqual(self.files("drafts"), [])
        self.assertIn("cr-162 - Python-quoted-upstream.md", self.files("completed"))
        self.assertIn("cr-187 - Records-upstream.md", self.files("tasks"))

    def test_is_migrated_matches_only_languages_ng(self):
        languages_ng.convert(self.repo, self.tracker, self.triage)
        self.assertTrue(languages_ng.is_migrated(self.backlog / "tasks" / "cr-531 - Disk.md"))
        self.assertFalse(languages_ng.is_migrated(self.backlog / "tasks" / "cr-187 - Records-upstream.md"))

    def test_main_writes_report(self):
        triage = Path(self._tmp.name) / "triage.json"
        triage.write_text(json.dumps(self.triage))
        report = Path(self._tmp.name) / "reports" / "languages-ng.md"
        status = languages_ng.main(["--repo", str(self.repo), "--tracker", str(self.tracker),
                                    "--triage", str(triage), "--report", str(report)])
        self.assertEqual(status, 0)
        self.assertTrue(report.read_text().startswith("# languages-ng migration report"))


if __name__ == "__main__":
    unittest.main()
