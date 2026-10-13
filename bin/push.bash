#!/usr/bin/env bash
# Push the change-request tracker (ourPLCC/change-requests): fetch, rebase
# onto origin/main, pass bin/check.py --pre-push, push. Holds a lock on this
# repo's root, which in a devcontainer is the ourplcc-dev volume's mount
# point, the same lock the code repos' bin/install/shared-clones.bash takes.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DEV_ROOT="$(dirname "${SCRIPT_DIR}")"
TRACKER="${OURPLCC_CHANGE_REQUESTS:-/workspaces/change-requests}"

die() {
    echo "push.bash: $*" >&2
    exit 1
}

git -C "${TRACKER}" rev-parse --git-dir >/dev/null 2>&1 \
    || die "${TRACKER} is not a git clone of ourPLCC/change-requests"

# Re-run under the lock. -o keeps the lock's descriptor in flock alone, so a
# child that outlives this script (git maintenance, detached by fetch) does
# not hold it; -w turns a stuck holder into an error.
# OURPLCC_LOCK_WAIT shortens the wait, for tests.
if [ -z "${OURPLCC_PUSH_LOCKED:-}" ]; then
    status=0
    OURPLCC_PUSH_LOCKED=1 flock -o -w "${OURPLCC_LOCK_WAIT:-120}" -E 75 \
        "${DEV_ROOT}" "$0" "$@" || status=$?
    [ "${status}" -ne 75 ] \
        || die "timed out waiting for the lock on ${DEV_ROOT};" \
               "another push or clone holds it"
    exit "${status}"
fi
unset OURPLCC_PUSH_LOCKED

cd "${TRACKER}"

[ "$(git symbolic-ref --quiet --short HEAD || true)" = main ] \
    || die "${TRACKER} is not on main; check out main first"
[ -z "$(git status --porcelain)" ] \
    || die "${TRACKER} has uncommitted changes; commit or discard them first"

git fetch --quiet origin
if ! git rebase --quiet origin/main; then
    git rebase --abort
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
    || die "push rejected; if another push landed since the fetch, run this again"
echo "push.bash: pushed"
