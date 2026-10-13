import fcntl
import os
import subprocess
import tempfile
import time
import unittest
from pathlib import Path

from tests.test_check import CONFIG, record

ROOT = Path(__file__).resolve().parent.parent
PUSH = ROOT / "bin" / "push.bash"


class PushTest(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.tmp = Path(tmp.name)
        self.origin = self.tmp / "origin.git"
        self.tracker = self.tmp / "tracker"
        self.other = self.tmp / "other"
        # Isolate from the user's git config (signing, helpers, hooksPath).
        self.env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
        self.env.update(
            GIT_CONFIG_GLOBAL=os.devnull,
            GIT_CONFIG_NOSYSTEM="1",
            GIT_AUTHOR_NAME="Test",
            GIT_AUTHOR_EMAIL="test@example.com",
            GIT_COMMITTER_NAME="Test",
            GIT_COMMITTER_EMAIL="test@example.com",
            OURPLCC_CHANGE_REQUESTS=str(self.tracker),
        )
        self.git("init", "-q", "--bare", "-b", "main", str(self.origin))
        seed = self.tmp / "seed"
        self.git("init", "-q", "-b", "main", str(seed))
        self.write(seed, "backlog/config.yml", CONFIG)
        self.write(seed, "backlog/completed/cr-999 - Seed.md",
                   record("CR-999", project=None, type_=None))
        self.commit(seed, "Seed")
        self.git("-C", str(seed), "push", "-q", str(self.origin), "main")
        self.git("clone", "-q", str(self.origin), str(self.tracker))
        self.git("clone", "-q", str(self.origin), str(self.other))

    def git(self, *args):
        return subprocess.run(["git", *args], env=self.env, check=True,
                              capture_output=True, text=True).stdout

    def write(self, repo, rel, text):
        path = repo / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text)

    def commit(self, repo, message):
        self.git("-C", str(repo), "add", "-A")
        self.git("-C", str(repo), "commit", "-q", "-m", message)

    def add_cr(self, repo, n, title="Title"):
        self.write(repo, f"backlog/tasks/cr-{n} - {title}.md", record(f"CR-{n}"))
        self.commit(repo, f"Create task CR-{n} {title}")

    def push_other(self):
        self.git("-C", str(self.other), "push", "-q", "origin", "main")

    def run_push(self):
        return subprocess.run([str(PUSH)], env=self.env, capture_output=True, text=True)

    def origin_log(self):
        return self.git("--git-dir", str(self.origin), "log", "--format=%s", "main")

    def test_pushes_local_commits(self):
        self.add_cr(self.tracker, 1000)
        result = self.run_push()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("Create task CR-1000 Title", self.origin_log())

    def test_rebases_onto_commits_pushed_elsewhere(self):
        self.add_cr(self.other, 1001)
        self.push_other()
        self.add_cr(self.tracker, 1000)
        result = self.run_push()
        self.assertEqual(result.returncode, 0, result.stderr)
        log = self.origin_log()
        self.assertIn("Create task CR-1000 Title", log)
        self.assertIn("Create task CR-1001 Title", log)
        self.assertEqual(self.git("-C", str(self.tracker), "rev-parse", "HEAD"),
                         self.git("--git-dir", str(self.origin), "rev-parse", "main"))

    def test_nothing_to_push_exits_zero(self):
        result = self.run_push()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("nothing to push", result.stdout)

    def test_refuses_uncommitted_changes(self):
        self.add_cr(self.tracker, 1000)
        self.write(self.tracker, "backlog/tasks/cr-1001 - Title.md", record("CR-1001"))
        result = self.run_push()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("uncommitted", result.stderr)
        self.assertNotIn("CR-1000", self.origin_log())

    def test_rebase_conflict_aborts_and_keeps_local_commits(self):
        self.write(self.other, "backlog/config.yml", CONFIG + "statuses: [a]\n")
        self.commit(self.other, "Other config")
        self.push_other()
        self.write(self.tracker, "backlog/config.yml", CONFIG + "statuses: [b]\n")
        self.commit(self.tracker, "Tracker config")
        result = self.run_push()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("conflicted", result.stderr)
        self.assertFalse((self.tracker / ".git" / "rebase-merge").exists())
        self.assertFalse((self.tracker / ".git" / "rebase-apply").exists())
        self.assertEqual(
            self.git("-C", str(self.tracker), "log", "-1", "--format=%s").strip(),
            "Tracker config")
        self.assertNotIn("Tracker config", self.origin_log())

    def test_duplicate_id_after_rebase_blocks_push(self):
        self.add_cr(self.other, 1000, title="Other")
        self.push_other()
        self.add_cr(self.tracker, 1000)
        result = self.run_push()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("duplicate id CR-1000", result.stderr)
        self.assertIn("backlog doctor --fix", result.stderr)
        self.assertNotIn("CR-1000 Title", self.origin_log())

    def test_rejected_push_says_run_again(self):
        hook = self.origin / "hooks" / "pre-receive"
        hook.parent.mkdir(exist_ok=True)
        hook.write_text("#!/bin/sh\nexit 1\n")
        hook.chmod(0o755)
        self.add_cr(self.tracker, 1000)
        result = self.run_push()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("run this again", result.stderr)

    def test_refuses_branch_other_than_main(self):
        self.git("-C", str(self.tracker), "switch", "-q", "-c", "topic")
        self.add_cr(self.tracker, 1000)
        result = self.run_push()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("not on main", result.stderr)
        self.assertNotIn("CR-1000", self.origin_log())

    def test_refuses_detached_head(self):
        self.git("-C", str(self.tracker), "switch", "-q", "--detach")
        result = self.run_push()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("not on main", result.stderr)

    def test_missing_tracker_clone_explains(self):
        self.env["OURPLCC_CHANGE_REQUESTS"] = str(self.tmp / "missing")
        result = self.run_push()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("not a git clone", result.stderr)

    def test_waits_for_the_lock(self):
        self.add_cr(self.tracker, 1000)
        fd = os.open(ROOT, os.O_RDONLY)
        try:
            fcntl.flock(fd, fcntl.LOCK_EX)
            proc = subprocess.Popen([str(PUSH)], env=self.env,
                                    stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            time.sleep(0.5)
            self.assertIsNone(proc.poll(), "push.bash ran while the lock was held")
            self.assertNotIn("CR-1000", self.origin_log())
        finally:
            fcntl.flock(fd, fcntl.LOCK_UN)
            os.close(fd)
        _, stderr = proc.communicate(timeout=30)
        self.assertEqual(proc.returncode, 0, stderr)
        self.assertIn("Create task CR-1000 Title", self.origin_log())

    def test_gives_up_on_a_stuck_lock(self):
        self.add_cr(self.tracker, 1000)
        self.env["OURPLCC_LOCK_WAIT"] = "1"
        fd = os.open(ROOT, os.O_RDONLY)
        try:
            fcntl.flock(fd, fcntl.LOCK_EX)
            result = self.run_push()
        finally:
            fcntl.flock(fd, fcntl.LOCK_UN)
            os.close(fd)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("timed out waiting for the lock", result.stderr)
        self.assertNotIn("CR-1000", self.origin_log())

    def test_child_that_outlives_it_does_not_keep_the_lock(self):
        # Stands in for the git maintenance a fetch detaches.
        hook = self.tracker / ".git" / "hooks" / "pre-push"
        hook.parent.mkdir(exist_ok=True)
        hook.write_text("#!/bin/sh\n(sleep 5 >/dev/null 2>&1 </dev/null &)\nexit 0\n")
        hook.chmod(0o755)
        self.add_cr(self.tracker, 1000)
        result = self.run_push()
        self.assertEqual(result.returncode, 0, result.stderr)
        fd = os.open(ROOT, os.O_RDONLY)
        try:
            fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)  # raises if still held
            fcntl.flock(fd, fcntl.LOCK_UN)
        finally:
            os.close(fd)


if __name__ == "__main__":
    unittest.main()
