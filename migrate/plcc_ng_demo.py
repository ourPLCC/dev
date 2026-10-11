"""Convert plcc-ng-demo's legacy dev-docs/issues/ tracker into Backlog.md files.

Usage: python3 -m migrate.plcc_ng_demo --repo PLCC_NG_DEMO --tracker TRACKER --triage FILE --report OUT

The demo's tracker is a copy of plcc-ng's, so this runs plcc-ng's converter with
the demo's profile.
"""
import sys

from migrate import plcc_ng
from migrate.plcc_ng import FOLDERS, expected_counts, load_issues  # noqa: F401 (driver API)

# No legacy number repeats, so the duplicate-number range is empty: a repeat stops the run.
PROFILE = plcc_ng.Profile("plcc-ng-demo", 800, 100, range(0),
                          {"plcc-ng": 0, "languages-ng": 500},
                          "https://github.com/ourPLCC/plcc-ng-demo")


def issue_refs(issues):
    return plcc_ng.issue_refs(issues, PROFILE)


def is_migrated(path):
    return plcc_ng.is_migrated(path, PROFILE)


def convert(repo_root, tracker_root, triage):
    return plcc_ng.convert(repo_root, tracker_root, triage, PROFILE)


def main(argv=None):
    return plcc_ng.main(argv, PROFILE, __doc__)


if __name__ == "__main__":
    sys.exit(main())
