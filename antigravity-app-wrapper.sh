#!/usr/bin/bash
# /usr/bin/antigravity-app — CLI wrapper for Antigravity App
#
# Reads user flags from $XDG_CONFIG_HOME/antigravity-app-flags.conf
# and delegates to the actual binary under /opt/antigravity-app/.

XDG_CONFIG_HOME=${XDG_CONFIG_HOME:-~/.config}

ANTIGRAVITY_APP_USER_FLAGS=""
if [[ -f $XDG_CONFIG_HOME/antigravity-app-flags.conf ]]; then
    ANTIGRAVITY_APP_USER_FLAGS="$(sed 's/#.*//' $XDG_CONFIG_HOME/antigravity-app-flags.conf | tr '\n' ' ')"
fi

if [[ -x /opt/antigravity-app/Antigravity ]]; then
    exec /opt/antigravity-app/Antigravity "$@" $ANTIGRAVITY_APP_USER_FLAGS
elif [[ -x /opt/antigravity-app/antigravity-app ]]; then
    exec /opt/antigravity-app/antigravity-app "$@" $ANTIGRAVITY_APP_USER_FLAGS
elif [[ -x /opt/antigravity-app/antigravity ]]; then
    exec /opt/antigravity-app/antigravity "$@" $ANTIGRAVITY_APP_USER_FLAGS
else
    echo "Error: Antigravity executable not found in /opt/antigravity-app/" >&2
    exit 1
fi
