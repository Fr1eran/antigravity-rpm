#!/usr/bin/bash
# /usr/bin/antigravity-ide — CLI wrapper for Antigravity IDE
#
# Reads user flags from $XDG_CONFIG_HOME/antigravity-ide-flags.conf
# and delegates to the actual binary under /opt/antigravity-ide/bin/.

XDG_CONFIG_HOME=${XDG_CONFIG_HOME:-~/.config}

if [[ -f $XDG_CONFIG_HOME/antigravity-ide-flags.conf ]]; then
    ANTIGRAVITY_IDE_USER_FLAGS="$(sed 's/#.*//' $XDG_CONFIG_HOME/antigravity-ide-flags.conf | tr '\n' ' ')"
fi

exec /opt/antigravity-ide/bin/antigravity-ide "$@" $ANTIGRAVITY_IDE_USER_FLAGS
