# Fully Automatic Local Updates

The rest of this repository automates everything up to "the RPM is published
in the COPR repo" (see the [main README](../README.md#-how-it-works)):
daily version check → spec update → commit/tag → COPR rebuild → published
package. That part requires no action from anyone.

The one remaining manual step is on each user's own machine: running
`sudo dnf upgrade` to actually install the new build. This directory closes
that last gap with `systemd --user` timers that check daily and install
updates automatically, with a desktop notification when they do.

## What it does

- `antigravity-ide-autoupdate.sh` & `antigravity-app-autoupdate.sh` — check `dnf check-update`;
  if a newer build is available, run `dnf upgrade -y <package>` and send a desktop notification.
- `antigravity-ide-autoupdate.timer` (10:00 local time) & `antigravity-app-autoupdate.timer` (10:30 local time) — run daily checks with randomized delays.
- Independent scoped `/etc/sudoers.d/antigravity-ide-autoupdate` and `/etc/sudoers.d/antigravity-app-autoupdate` rules grant `NOPASSWD` for **exactly**
  `/usr/bin/dnf upgrade -y antigravity-ide` and `/usr/bin/dnf upgrade -y antigravity-app` — nothing broader.

## Install

```bash
# Set up auto-updates for both packages:
./install.sh all

# Or set up for a specific package only:
./install.sh ide
./install.sh app
```

This is interactive on purpose: it needs your sudo password once to write
the scoped sudoers rule. After that single run, updates are fully automatic.

## Uninstall

```bash
# Disable timers
systemctl --user disable --now antigravity-ide-autoupdate.timer antigravity-app-autoupdate.timer 2>/dev/null || true

# Remove unit files and scripts
rm -f ~/.config/systemd/user/antigravity-*-autoupdate.{service,timer}
rm -f ~/.local/bin/antigravity-*-autoupdate.sh
systemctl --user daemon-reload

# Remove sudoers rules
sudo rm -f /etc/sudoers.d/antigravity-ide-autoupdate /etc/sudoers.d/antigravity-app-autoupdate /etc/sudoers.d/antigravity-autoupdate
```
