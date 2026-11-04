#!/bin/bash
# ============================================================================
# antigravity-app-autoupdate.sh — check for and install antigravity-app
# updates via dnf, notifying the desktop session on success.
#
# Run periodically by the antigravity-app-autoupdate systemd --user timer.
# Requires a scoped NOPASSWD sudo rule for exactly:
#   /usr/bin/dnf upgrade -y antigravity-app
# (installed by install.sh into /etc/sudoers.d/).
# ============================================================================

set -uo pipefail

PACKAGE="antigravity-app"
LOG_TAG="antigravity-app-autoupdate"

log() {
    logger -t "$LOG_TAG" -- "$1"
    echo "$1"
}

if ! rpm -q "$PACKAGE" >/dev/null 2>&1; then
    log "$PACKAGE is not installed; nothing to do"
    exit 0
fi

OLD_VERSION=$(rpm -q --qf '%{VERSION}-%{RELEASE}' "$PACKAGE")

dnf check-update -q "$PACKAGE" >/dev/null 2>&1
RC=$?

if [[ $RC -eq 0 ]]; then
    log "no update available (current: $OLD_VERSION)"
    exit 0
elif [[ $RC -eq 1 ]]; then
    log "dnf check-update failed for $PACKAGE"
    exit 1
fi
# RC == 100 means an update is available; fall through.

log "update available for $PACKAGE (current: $OLD_VERSION), upgrading..."

UPGRADE_LOG=$(mktemp)
if ! sudo -n /usr/bin/dnf upgrade -y "$PACKAGE" >"$UPGRADE_LOG" 2>&1; then
    log "dnf upgrade failed for $PACKAGE, see $UPGRADE_LOG"
    exit 1
fi
rm -f "$UPGRADE_LOG"

NEW_VERSION=$(rpm -q --qf '%{VERSION}-%{RELEASE}' "$PACKAGE")
log "upgraded $PACKAGE: $OLD_VERSION -> $NEW_VERSION"

if command -v notify-send >/dev/null 2>&1; then
    notify-send -i software-update-available \
        "Antigravity App updated" \
        "Updated to version ${NEW_VERSION}. Restart the app to use it."
fi
