"""The legacy-tracker drivers, one per migrated repo, by project name."""
import importlib

DRIVERS = {"plcc-ng": "migrate.plcc_ng", "languages-ng": "migrate.languages_ng"}


def load(project):
    return importlib.import_module(DRIVERS[project])
