#!/bin/bash
# ============================================================================
# install.sh — Set up fully automatic local updates for Antigravity packages.
#
# Usage:
#   ./install.sh [all|ide|app]   (default: all)
#
# Installs:
#   - ~/.local/bin/antigravity-{ide,app}-autoupdate.sh
#   - ~/.config/systemd/user/antigravity-{ide,app}-autoupdate.{service,timer}
#   - /etc/sudoers.d/antigravity-ide-autoupdate (scoped NOPASSWD rule for IDE)
#   - /etc/sudoers.d/antigravity-app-autoupdate (scoped NOPASSWD rule for App)
#
# Run this once, interactively, as the user who should receive updates.
# It will prompt for your sudo password to install the sudoers rule(s).
# ============================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TARGET_USER="$(id -un)"
TARGET="${1:-all}"

INSTALL_IDE=false
INSTALL_APP=false

case "$TARGET" in
    ide)
        INSTALL_IDE=true
        ;;
    app)
        INSTALL_APP=true
        ;;
    all|"")
        INSTALL_IDE=true
        INSTALL_APP=true
        ;;
    *)
        echo "Usage: $0 [all|ide|app]" >&2
        exit 1
        ;;
esac

mkdir -p "$HOME/.local/bin"
mkdir -p "$HOME/.config/systemd/user"

install_sudoers_rule() {
    local pkg="$1"
    local filename="antigravity-${pkg}-autoupdate"
    local tmp_file
    tmp_file="$(mktemp)"
    
    cat > "$tmp_file" <<EOF
# Installed by antigravity-rpm/local-autoupdate/install.sh
# Scoped NOPASSWD rule for automatic update of ${pkg} for ${TARGET_USER}.
${TARGET_USER} ALL=(root) NOPASSWD: /usr/bin/dnf upgrade -y antigravity-${pkg}
EOF

    echo "==> Preparing scoped sudoers rule for antigravity-${pkg} (requires sudo password)"
    sudo visudo -c -f "$tmp_file"
    sudo install -m 0440 -o root -g root "$tmp_file" "/etc/sudoers.d/${filename}"
    rm -f "$tmp_file"
    echo "    Installed /etc/sudoers.d/${filename}"
}

if [[ "$INSTALL_IDE" == "true" ]]; then
    echo "==> Configuring autoupdate for Antigravity IDE"
    install -m 755 "$SCRIPT_DIR/antigravity-ide-autoupdate.sh" "$HOME/.local/bin/antigravity-ide-autoupdate.sh"
    install -m 644 "$SCRIPT_DIR/antigravity-ide-autoupdate.service" "$HOME/.config/systemd/user/antigravity-ide-autoupdate.service"
    install -m 644 "$SCRIPT_DIR/antigravity-ide-autoupdate.timer" "$HOME/.config/systemd/user/antigravity-ide-autoupdate.timer"
    install_sudoers_rule "ide"
fi

if [[ "$INSTALL_APP" == "true" ]]; then
    echo "==> Configuring autoupdate for Antigravity App"
    install -m 755 "$SCRIPT_DIR/antigravity-app-autoupdate.sh" "$HOME/.local/bin/antigravity-app-autoupdate.sh"
    install -m 644 "$SCRIPT_DIR/antigravity-app-autoupdate.service" "$HOME/.config/systemd/user/antigravity-app-autoupdate.service"
    install -m 644 "$SCRIPT_DIR/antigravity-app-autoupdate.timer" "$HOME/.config/systemd/user/antigravity-app-autoupdate.timer"
    install_sudoers_rule "app"
fi

# Clean up legacy merged sudoers file if it exists
if [[ -f /etc/sudoers.d/antigravity-autoupdate ]]; then
    sudo rm -f /etc/sudoers.d/antigravity-autoupdate 2>/dev/null || true
fi

echo "==> Enabling systemd --user timer(s)"
systemctl --user daemon-reload

if [[ "$INSTALL_IDE" == "true" ]]; then
    systemctl --user enable --now antigravity-ide-autoupdate.timer
fi
if [[ "$INSTALL_APP" == "true" ]]; then
    systemctl --user enable --now antigravity-app-autoupdate.timer
fi

echo
echo "Done. Active timers:"
systemctl --user list-timers "antigravity-*" --no-pager
