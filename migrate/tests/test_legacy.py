import tempfile
import textwrap
import unittest
from pathlib import Path

from migrate.legacy import parse_frontmatter_issue, parse_issue

SAMPLE = textwrap.dedent("""\
    # 035 - plcc-diagram: output `x` hangs

    **Type:** Bug (regression)
    **Date:** 2026-05-01
    **Status:** abandoned — superseded by #124
    **Supersedes:** #012

    <!--
    Classify by user-facing impact, not by whether something was "broken".
    -->

    ## Description

    It hangs.

    ```text
    ## not a heading
    ```

    ## Steps to Reproduce

    1. Run it.

    ### Detail

    More.

    ## Notes

    See #036.
    """)


class ParseIssueTest(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.repo = Path(self._tmp.name)
        done = self.repo / "dev-docs" / "issues" / "done"
        done.mkdir(parents=True)
        self.path = done / "035-plcc-diagram-output-build-hangs.md"
        self.path.write_text(SAMPLE)
        self.issue = parse_issue(self.path, self.repo)

    def tearDown(self):
        self._tmp.cleanup()

    def test_identity_fields(self):
        self.assertEqual(self.issue.number, 35)
        self.assertEqual(self.issue.slug, "plcc-diagram-output-build-hangs")
        self.assertEqual(self.issue.rel_path, "dev-docs/issues/done/035-plcc-diagram-output-build-hangs.md")
        self.assertTrue(self.issue.closed)

    def test_header_fields(self):
        self.assertEqual(self.issue.title, "plcc-diagram: output `x` hangs")
        self.assertEqual(self.issue.type, "bug")
        self.assertEqual(self.issue.date, "2026-05-01")
        self.assertEqual(self.issue.status_note, "abandoned — superseded by #124")

    def test_preamble_keeps_other_bold_lines_and_drops_template_comment(self):
        self.assertIn("**Supersedes:** #012", self.issue.preamble)
        self.assertNotIn("Classify", self.issue.preamble)
        self.assertNotIn("**Type:**", self.issue.preamble)

    def test_sections_split_on_level_two_headings_outside_fences(self):
        headings = [h for h, _ in self.issue.sections]
        self.assertEqual(headings, ["Description", "Steps to Reproduce", "Notes"])
        description = dict(self.issue.sections)["Description"]
        self.assertIn("## not a heading", description)
        self.assertIn("### Detail", dict(self.issue.sections)["Steps to Reproduce"])

    def test_open_issue_is_not_closed(self):
        path = self.repo / "dev-docs" / "issues" / "160-race.md"
        path.write_text("# 160 - Race\n\n**Type:** fix\n**Date:** 2026-07-01\n\n## Description\n\nX.\n")
        issue = parse_issue(path, self.repo)
        self.assertFalse(issue.closed)
        self.assertEqual(issue.status_note, "")
        self.assertEqual(issue.preamble, "")

    def test_bad_title_line_raises(self):
        path = self.repo / "dev-docs" / "issues" / "161-bad.md"
        path.write_text("Not a title\n")
        with self.assertRaises(ValueError):
            parse_issue(path, self.repo)


LN_SAMPLE = textwrap.dedent("""\
    ---
    type: chore
    target: ourPLCC/plcc-ng
    upstream: ourPLCC/plcc-ng 188-follow-set.md
    opened: 2026-08-11
    closed: 2026-08-12
    ---

    # 038 - FOLLOW set omits the nullable tail

    <!--
    `type` is a conventional commit type. Classify by user-facing impact, not
    by whether something was "broken".
    -->

    ## Summary

    One paragraph.

    ## Description

    It breaks.

    ```text
    ## Summary
    ```

    ## Notes

    See #6.
    """)


class FrontmatterIssueTest(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.repo = Path(self._tmp.name)
        self.issues = self.repo / "dev-docs" / "issues"
        self.issues.mkdir(parents=True)

    def tearDown(self):
        self._tmp.cleanup()

    def parse(self, text=LN_SAMPLE, name="038-follow-set.md"):
        path = self.issues / name
        path.write_text(text)
        return parse_frontmatter_issue(path, self.repo)

    def test_fields(self):
        issue = self.parse()
        self.assertEqual((issue.number, issue.slug, issue.title),
                         (38, "follow-set", "FOLLOW set omits the nullable tail"))
        self.assertEqual((issue.type, issue.target, issue.date),
                         ("chore", "ourPLCC/plcc-ng", "2026-08-11"))
        self.assertTrue(issue.closed)
        self.assertEqual(issue.status_note, "")
        self.assertEqual(issue.rel_path, "dev-docs/issues/038-follow-set.md")

    def test_summary_leads_and_template_comment_is_dropped(self):
        issue = self.parse()
        self.assertEqual(issue.preamble, "### Summary\n\nOne paragraph.")
        self.assertEqual([heading for heading, _ in issue.sections], ["Description", "Notes"])
        self.assertIn("## Summary", issue.sections[0][1])
        everything = issue.preamble + "".join(body for _, body in issue.sections)
        self.assertNotIn("Classify", everything)

    def test_empty_closed_means_open(self):
        self.assertFalse(self.parse(LN_SAMPLE.replace("closed: 2026-08-12", "closed:")).closed)

    def test_empty_summary_is_dropped(self):
        self.assertEqual(self.parse(LN_SAMPLE.replace("One paragraph.\n", "")).preamble, "")

    def test_unknown_or_missing_key_is_an_error(self):
        for old, new in (("closed: 2026-08-12", "closed: 2026-08-12\npriority: high"),
                         ("target: ourPLCC/plcc-ng\n", "")):
            with self.subTest(new=new):
                with self.assertRaises(ValueError) as cm:
                    self.parse(LN_SAMPLE.replace(old, new))
                self.assertIn("038-follow-set.md", str(cm.exception))

    def test_title_number_must_match_filename(self):
        with self.assertRaises(ValueError):
            self.parse(name="039-follow-set.md")

    def test_bad_opened_date_is_an_error(self):
        with self.assertRaises(ValueError):
            self.parse(LN_SAMPLE.replace("opened: 2026-08-11", "opened: YYYY-MM-DD"))


if __name__ == "__main__":
    unittest.main()
