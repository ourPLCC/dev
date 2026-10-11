import tempfile
import textwrap
import unittest
from pathlib import Path

from migrate import drivers, plcc_ng, plcc_ng_demo, repo_links
from migrate.emit import render_task


def legacy(number, title, type_="fix", body="Body."):
    return textwrap.dedent(f"""\
        # {number:03d} - {title}

        **Type:** {type_}
        **Date:** 2026-07-21
        """) + f"\n## Description\n\n{body}\n\n## Notes\n\nN.\n"


class PlccNgDemoTest(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        base = Path(self._tmp.name)
        self.repo, self.tracker = base / "plcc-ng-demo", base / "tracker"
        done = self.repo / "dev-docs" / "issues" / "done"
        done.mkdir(parents=True)
        files = {
            "001-migration-docs.md": legacy(1, "Migration docs", "docs"),
            "002-race.md": legacy(2, "Race", "fix", body="Unlike #3, see plcc-ng #160."),
            "003-div.md": legacy(3, "Div", "docs", body="See #1 and languages-ng #12."),
        }
        for name, text in files.items():
            (done / name).write_text(text)
        (self.repo / "dev-docs" / "issues" / "TEMPLATE.md").write_text("# NNN - Title\n")
        self.backlog = self.tracker / "backlog"
        for folder in ("tasks", "completed", "drafts"):
            (self.backlog / folder).mkdir(parents=True)
        self.write_cr("completed", 159, "Migration docs upstream", "docs", "Done")
        self.write_cr("tasks", 160, "Race upstream", "feat", "To Do")
        self.triage = {"open": {}, "duplicates": {"1": 159, "2": 160}}

    def tearDown(self):
        self._tmp.cleanup()

    def write_cr(self, folder, cr, title, type_, status):
        description = f"Upstream.\n\nMigrated from plcc-ng #{cr:03d}."
        (self.backlog / folder / f"cr-{cr} - {title.replace(' ', '-')}.md").write_text(
            render_task(task_id=f"CR-{cr}", title=title, status=status, created="2026-07-22",
                        labels=[], description=description, type_=type_, project="plcc-ng"))

    def files(self, folder):
        return sorted(p.name for p in (self.backlog / folder).glob("*.md"))

    def read(self, folder, name):
        return (self.backlog / folder / name).read_text()

    def test_registered_driver(self):
        self.assertIs(drivers.load("plcc-ng-demo"), plcc_ng_demo)

    def test_issue_refs_use_offset_800(self):
        refs = plcc_ng_demo.issue_refs(plcc_ng_demo.load_issues(self.repo))
        self.assertEqual(refs[3][0].cr, 803)

    def test_expected_counts(self):
        self.assertEqual(plcc_ng_demo.expected_counts(plcc_ng_demo.load_issues(self.repo), self.triage),
                         {"tasks": 0, "completed": 3, "drafts": 0})

    def test_convert_places_files(self):
        plcc_ng_demo.convert(self.repo, self.tracker, self.triage)
        self.assertEqual(self.files("completed"),
                         ["cr-159 - Migration-docs-upstream.md", "cr-801 - Migration-docs.md",
                          "cr-802 - Race.md", "cr-803 - Div.md"])
        self.assertEqual(self.files("tasks"), ["cr-160 - Race-upstream.md"])

    def test_duplicates_are_wontdo_with_the_plcc_ng_type(self):
        report = plcc_ng_demo.convert(self.repo, self.tracker, self.triage)
        race = self.read("completed", "cr-802 - Race.md")
        for expected in ("status: Done", "  - wontdo", "type: feat", "project: plcc-ng",
                         "Duplicate of CR-160, filed upstream by hand.",
                         "Migrated from plcc-ng-demo #002."):
            self.assertIn(expected, race)
        self.assertIn("#002 -> CR-802: duplicate of CR-160", report)

    def test_local_issue_content(self):
        plcc_ng_demo.convert(self.repo, self.tracker, self.triage)
        div = self.read("completed", "cr-803 - Div.md")
        for expected in ("status: Done", "type: docs", "project: plcc-ng-demo",
                         "See CR-801 and languages-ng CR-512.", "Migrated from plcc-ng-demo #003."):
            self.assertIn(expected, div)
        self.assertNotIn("wontdo", div)
        race = self.read("completed", "cr-802 - Race.md")
        self.assertIn("Unlike CR-803, see plcc-ng CR-160.", race)

    def test_duplicate_of_missing_cr(self):
        self.triage["duplicates"]["3"] = 999
        with self.assertRaises(SystemExit) as cm:
            plcc_ng_demo.convert(self.repo, self.tracker, self.triage)
        self.assertIn("CR-999", str(cm.exception))

    def test_duplicate_key_that_is_not_an_issue(self):
        self.triage["duplicates"]["7"] = 159
        with self.assertRaises(SystemExit) as cm:
            plcc_ng_demo.convert(self.repo, self.tracker, self.triage)
        self.assertIn("'7'", str(cm.exception))

    def test_provenance_is_per_repo(self):
        plcc_ng_demo.convert(self.repo, self.tracker, self.triage)
        demo = self.backlog / "completed" / "cr-803 - Div.md"
        upstream = self.backlog / "completed" / "cr-159 - Migration-docs-upstream.md"
        self.assertTrue(plcc_ng_demo.is_migrated(demo))
        self.assertFalse(plcc_ng_demo.is_migrated(upstream))
        self.assertFalse(plcc_ng.is_migrated(demo))
        self.assertTrue(plcc_ng.is_migrated(upstream))

    def test_rerun_keeps_plcc_ng_crs(self):
        plcc_ng_demo.convert(self.repo, self.tracker, self.triage)
        plcc_ng_demo.convert(self.repo, self.tracker, self.triage)
        self.assertIn("cr-159 - Migration-docs-upstream.md", self.files("completed"))
        self.assertEqual(self.files("tasks"), ["cr-160 - Race-upstream.md"])

    def test_report(self):
        report = plcc_ng_demo.convert(self.repo, self.tracker, self.triage)
        self.assertTrue(report.startswith("# plcc-ng-demo migration report"))
        self.assertIn("Converted 3 files: 3 -> completed/, 0 -> tasks/, 0 -> drafts/.", report)

    def test_main_writes_report(self):
        triage = self.tracker / "triage.json"
        triage.write_text('{"open": {}, "duplicates": {"1": 159, "2": 160}}')
        out = self.tracker / "reports" / "plcc-ng-demo.md"
        self.assertEqual(plcc_ng_demo.main(["--repo", str(self.repo), "--tracker", str(self.tracker),
                                            "--triage", str(triage), "--report", str(out)]), 0)
        self.assertIn("duplicate of CR-159", out.read_text())

    def test_repo_links_rewrite_to_demo_crs(self):
        doc = self.repo / "dev-docs" / "notes.md"
        doc.write_text("See [the race](issues/done/002-race.md).\n")
        changed, _ = repo_links.rewrite_repo(self.repo, "plcc-ng-demo")
        self.assertEqual(changed, ["dev-docs/notes.md"])
        self.assertEqual(doc.read_text(), "See the race (CR-802).\n")


if __name__ == "__main__":
    unittest.main()
