#!/usr/bin/env bash
# Push the change-request tracker (ourPLCC/change-requests): fetch, rebase
# onto origin/main, pass bin/check.py --pre-push, push. Holds a lock on the
# ourplcc-dev volume's mount point, /workspaces/dev, the same lock the code
# repos' bin/install/shared-clones.bash takes.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DEV_ROOT="$(dirname "${SCRIPT_DIR}")"
TRACKER="${OURPLCC_CHANGE_REQUESTS:-/workspaces/change-requests}"
LOCK_DIR="${OURPLCC_LOCK_DIR:-/workspaces/dev}"

die() {
    echo "push.bash: $*" >&2
    exit 1
}

git -C "${TRACKER}" rev-parse --verify --quiet HEAD >/dev/null 2>&1 \
    || die "${TRACKER} is not a git clone of ourPLCC/change-requests" \
           "(missing, empty, or an unfinished clone);" \
           "rerun bin/install/shared-clones.bash"

# Re-run under the lock. -o keeps the lock's descriptor in flock alone, so a
# child that outlives this script (git maintenance, detached by fetch) does
# not hold it; -w turns a stuck holder into an error.
# OURPLCC_LOCK_DIR and OURPLCC_LOCK_WAIT are for tests.
if [ -z "${OURPLCC_PUSH_LOCKED:-}" ]; then
    status=0
    OURPLCC_PUSH_LOCKED=1 flock -o -w "${OURPLCC_LOCK_WAIT:-120}" -E 75 \
        "${LOCK_DIR}" bash "${BASH_SOURCE[0]}" "$@" || status=$?
    [ "${status}" -ne 75 ] \
        || die "timed out waiting for the lock on ${LOCK_DIR};" \
               "another push or clone holds it"
    exit "${status}"
fi
unset OURPLCC_PUSH_LOCKED

cd "${TRACKER}"

rebase_in_progress() {
    [ -d "$(git rev-parse --git-path rebase-merge)" ] \
        || [ -d "$(git rev-parse --git-path rebase-apply)" ]
}

! rebase_in_progress \
    || die "a rebase is in progress in ${TRACKER}; finish it" \
           "(git rebase --continue) or run 'git rebase --abort', then run this again"
[ "$(git symbolic-ref --quiet --short HEAD || true)" = main ] \
    || die "${TRACKER} is not on main; check out main first"
[ -z "$(git status --porcelain)" ] \
    || die "${TRACKER} has uncommitted changes; commit or discard them first"

git fetch --quiet origin
if ! git rebase --quiet origin/main; then
    rebase_in_progress \
        || die "rebase onto origin/main failed (see git's message above);" \
               "nothing changed; run this again"
    git rebase --abort \
        || die "rebase onto origin/main conflicted and could not be aborted;" \
               "run 'git rebase --abort' in ${TRACKER}"
    die "rebase onto origin/main conflicted; aborted, local commits kept." \
        "Resolve with 'git pull --rebase' in ${TRACKER}, then run this again"
fi

python3 "${DEV_ROOT}/bin/check.py" --pre-push --root "${TRACKER}" \
    || die "bin/check.py failed; nothing pushed. For a duplicate id," \
           "run 'backlog doctor --fix', commit, and run this again"

if [ "$(git rev-list --count origin/main..HEAD)" -eq 0 ]; then
    echo "push.bash: nothing to push"
    exit 0
fi

git push --quiet origin main \
    || die "push failed (see git's message above). If another push landed" \
           "since the fetch, run this again; if it is an authentication error," \
           "see 'Your token' in dev's CONTRIBUTING.md"
echo "push.bash: pushed"
