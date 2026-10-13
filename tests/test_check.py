import importlib.util
import subprocess
import sys
import tempfile
import textwrap
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
_spec = importlib.util.spec_from_file_location("check", ROOT / "bin" / "check.py")
check = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(check)

CONFIG = textwrap.dedent("""\
    labels: ["wontdo"]
    types: ["fix", "feat", "docs", "test", "refactor", "chore"]
    projects: ["plcc-ng", "languages-ng"]
    task_prefix: "cr"
    """)


def record(id_, *, project="plcc-ng", type_="fix", labels=(), body="Why."):
    lines = ["---", f"id: {id_}", "title: 'A: title'", "status: To Do", "assignee: []"]
    if labels:
        lines.append("labels:")
        lines += [f"  - {label}" for label in labels]
    else:
        lines.append("labels: []")
    lines.append("dependencies: []")
    if type_ is not None:
        lines.append(f"type: {type_}")
    if project is not None:
        lines.append(f"project: {project}")
    lines += ["---", "", "## Description", "", body, ""]
    return "\n".join(lines)


class CheckTest(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name)
        (self.root / "backlog").mkdir()
        (self.root / "backlog" / "config.yml").write_text(CONFIG)
        self.add("completed", "cr-999 - Seed.md", record("CR-999", project=None, type_=None))

    def tearDown(self):
        self._tmp.cleanup()

    def add(self, folder, name, text):
        path = self.root / "backlog" / folder / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text)
        return path

    def errors(self, **kw):
        return check.check(self.root, **kw)

    def assertError(self, fragment, **kw):
        errors = self.errors(**kw)
        self.assertTrue(any(fragment in e for e in errors), f"{fragment!r} not in {errors}")

    def test_clean_tracker_passes(self):
        self.add("tasks", "cr-1000 - A.md", record("CR-1000"))
        self.add("completed", "cr-160 - B.md", record("CR-160", labels=["wontdo"]))
        self.add("drafts", "draft-1 - Idea.md", record("DRAFT-1", body="DRAFT-1 is me."))
        self.assertEqual(self.errors(), [])

    def test_duplicate_id_across_folders(self):
        self.add("tasks", "cr-5 - A.md", record("CR-5"))
        self.add("completed", "cr-5 - B.md", record("CR-5"))
        self.assertError("duplicate id CR-5")

    def test_filename_id_mismatch(self):
        self.add("tasks", "cr-7 - A.md", record("CR-8"))
        self.assertError("filename does not match id")

    def test_draft_cited_elsewhere(self):
        self.add("drafts", "draft-3 - Idea.md", record("DRAFT-3"))
        self.add("tasks", "cr-1000 - A.md", record("CR-1000", body="See DRAFT-3."))
        self.assertError("cites DRAFT-3")

    def test_missing_project(self):
        self.add("tasks", "cr-1000 - A.md", record("CR-1000", project=None))
        self.assertError("project")

    def test_unknown_project(self):
        self.add("tasks", "cr-1000 - A.md", record("CR-1000", project="nope"))
        self.assertError("project 'nope'")

    def test_missing_type(self):
        self.add("tasks", "cr-1000 - A.md", record("CR-1000", type_=None))
        self.assertError("type None")

    def test_unknown_type(self):
        self.add("tasks", "cr-1000 - A.md", record("CR-1000", type_="ci"))
        self.assertError("type 'ci'")

    def test_unknown_label(self):
        self.add("tasks", "cr-1000 - A.md", record("CR-1000", labels=["typo"]))
        self.assertError("label 'typo'")

    def test_archived_file_fails(self):
        self.add("archive/tasks", "cr-1000 - A.md", record("CR-1000"))
        self.assertError("archived file")

    def test_pre_push_flags_uncommitted_changes(self):
        git = ["git", "-c", "user.name=t", "-c", "user.email=t@t", "-C", str(self.root)]
        subprocess.run(git + ["init", "-q"], check=True)
        subprocess.run(git + ["add", "-A"], check=True)
        subprocess.run(git + ["commit", "-q", "-m", "x"], check=True)
        self.add("tasks", "cr-1000 - A.md", record("CR-1000"))
        self.assertEqual(self.errors(), [])
        self.assertError("uncommitted change under backlog/", pre_push=True)

    def test_pre_push_flags_untracked_even_if_host_hides_them(self):
        git = ["git", "-c", "user.name=t", "-c", "user.email=t@t", "-C", str(self.root)]
        subprocess.run(git + ["init", "-q"], check=True)
        subprocess.run(git + ["config", "status.showUntrackedFiles", "no"], check=True)
        subprocess.run(git + ["add", "-A"], check=True)
        subprocess.run(git + ["commit", "-q", "--allow-empty", "-m", "x"], check=True)
        self.add("tasks", "cr-1000 - A.md", record("CR-1000"))
        self.assertError("uncommitted change under backlog/", pre_push=True)

    def test_quoted_scalars_parse(self):
        fm = check.parse_frontmatter("---\ntitle: 'A: b ''c'''\nid: CR-1\n---\n")
        self.assertEqual(fm["title"], "A: b 'c'")
        self.assertEqual(fm["id"], "CR-1")

    def test_cli_runs_without_backlog_on_path(self):
        self.add("tasks", "cr-1000 - A.md", record("CR-1000"))
        result = subprocess.run(
            [sys.executable, str(ROOT / "bin" / "check.py"), "--root", str(self.root)],
            env={"PATH": "/nonexistent"}, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("check: ok", result.stdout)

    def test_cli_exit_code_on_error(self):
        self.add("tasks", "cr-1000 - A.md", record("CR-1000", project="nope"))
        result = subprocess.run(
            [sys.executable, str(ROOT / "bin" / "check.py"), "--root", str(self.root)],
            capture_output=True, text=True)
        self.assertEqual(result.returncode, 1)
        self.assertIn("check: ", result.stderr)

    def test_cli_requires_root(self):
        result = subprocess.run(
            [sys.executable, str(ROOT / "bin" / "check.py")],
            capture_output=True, text=True)
        self.assertEqual(result.returncode, 2)
        self.assertIn("--root", result.stderr)
        self.assertNotIn("Traceback", result.stderr)

    def test_root_without_tracker_is_a_clear_error(self):
        empty = self.root / "not-a-tracker"
        empty.mkdir()
        result = subprocess.run(
            [sys.executable, str(ROOT / "bin" / "check.py"), "--root", str(empty)],
            capture_output=True, text=True)
        self.assertEqual(result.returncode, 1)
        self.assertIn("no backlog/config.yml", result.stderr)
        self.assertNotIn("Traceback", result.stderr)

    def hook(self, name):
        git = ["git", "-c", "user.name=t", "-c", "user.email=t@t", "-C", str(self.root)]
        subprocess.run(git + ["init", "-q"], check=True)
        subprocess.run(git + ["add", "-A"], check=True)
        subprocess.run(git + ["commit", "-q", "-m", "x"], check=True)
        return subprocess.run(["sh", str(ROOT / ".githooks" / name)],
                              cwd=self.root, capture_output=True, text=True)

    def test_pre_commit_hook_checks_the_repo_that_runs_it(self):
        self.add("tasks", "cr-1000 - A.md", record("CR-1000", project="nope"))
        result = self.hook("pre-commit")
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn("project", result.stderr)

    def test_pre_push_hook_checks_the_repo_that_runs_it(self):
        result = self.hook("pre-push")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.add("tasks", "cr-1000 - A.md", record("CR-1000"))
        result = subprocess.run(["sh", str(ROOT / ".githooks" / "pre-push")],
                                cwd=self.root, capture_output=True, text=True)
        self.assertEqual(result.returncode, 1)
        self.assertIn("uncommitted change under backlog/", result.stderr)


if __name__ == "__main__":
    unittest.main()
