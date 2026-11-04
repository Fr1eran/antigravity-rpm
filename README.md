# Antigravity (IDE & App) — Fedora RPM (COPR)

[![Copr build status (IDE)](https://copr.fedorainfracloud.org/coprs/fr1eran/antigravity-rpm/package/antigravity-ide/status_image/last_build.png)](https://copr.fedorainfracloud.org/coprs/fr1eran/antigravity-rpm/)
[![Copr build status (App)](https://copr.fedorainfracloud.org/coprs/fr1eran/antigravity-rpm/package/antigravity-app/status_image/last_build.png)](https://copr.fedorainfracloud.org/coprs/fr1eran/antigravity-rpm/)
[![Daily Update Check (IDE)](https://github.com/Fr1eran/antigravity-rpm/actions/workflows/check-update-ide.yml/badge.svg)](https://github.com/Fr1eran/antigravity-rpm/actions/workflows/check-update-ide.yml)
[![Daily Update Check (App)](https://github.com/Fr1eran/antigravity-rpm/actions/workflows/check-update-app.yml/badge.svg)](https://github.com/Fr1eran/antigravity-rpm/actions/workflows/check-update-app.yml)

Unofficial community RPM packaging of [Google Antigravity](https://antigravity.google) (Antigravity IDE & Antigravity App) for Fedora. Enables native installation and automatic updates via `dnf`.

> **⚠️ Disclaimer**: This is an **unofficial**, community-maintained package. Google Antigravity is proprietary software developed by Google. This repository contains only the packaging scripts (spec files, desktop entries, automation) — the binaries are **never stored here** and are downloaded directly from Google's servers during the RPM build process. This project is not affiliated with, endorsed by, or sponsored by Google.

---

## 🚀 Quick Install

```bash
# Enable the COPR repository
sudo dnf copr enable fr1eran/antigravity-rpm

# Install Antigravity IDE 
sudo dnf install antigravity-ide

# Install Antigravity App
sudo dnf install antigravity-app
```

## 🔄 Keeping Antigravity Updated

Once the COPR repo is enabled (see Quick Install above), staying current is
just:

```bash
sudo dnf upgrade
```

Run whenever you like — weekly, or as part of your normal `sudo dnf upgrade`
habit alongside the rest of your system. There's no separate channel or
extra repo to remember: `antigravity-ide` and `antigravity-app` upgrade exactly like any other
`dnf`-managed package, because a daily pipeline behind the scenes keeps the
COPR repo itself current (see **How It Works** below), so the new build is
usually already sitting in the repo by the time you run the command.

If you want that last mile automated too — no need to even remember to run
`dnf upgrade` — see [`local-autoupdate/`](local-autoupdate/): a one-time
`./install.sh` sets up a `systemd --user` timer that checks daily and
installs new builds automatically, with a desktop notification when it does.

### Why doesn't the app itself tell me when an update is available?

It deliberately doesn't, on purpose. Antigravity bundles Electron / VS Code's own
in-app updater, which independently pings a Google-owned endpoint and shows
its own "update available" banner — a mechanism this packaging has no
control over and that isn't aware of what's actually published in this COPR
repo. Left alone, it produces confusing false positives (a notification
telling you to update even when you're already on the latest COPR build).
This package clears `product.json`'s `updateUrl` at build time, which is the
sanctioned way VS Code-based apps disable their built-in updater — so `dnf`
is the one and only source of truth for whether a new version is available.
If you ever see an in-app "update available" notification, it's stale
cache from before this fix (`2.1.1-2`+); `sudo dnf upgrade` is always the
authoritative answer.

## 🏗️ How It Works

```
┌────────────────────┐     ┌─────────────────────┐     ┌────────────────────┐
│  GitHub Actions    │────▶│  Detects new        │────▶│  Updates spec      │
│  (daily cron)      │     │  version upstream   │     │  + commits + tags  │
└────────────────────┘     └─────────────────────┘     └──────────┬─────────┘
                                                                   │
                                                                   ▼
┌────────────────────┐     ┌─────────────────────┐     ┌────────────────────┐
│  dnf upgrade       │◀────│  RPM available      │◀────│  COPR builds       │
│  installs it       │     │  in the COPR repo   │     │  RPM from spec     │
└────────────────────┘     └─────────────────────┘     └────────────────────┘
```

Everything from "new version exists" to "the RPM is sitting in the COPR
repo" runs unattended, with no human in the loop:

1. **Daily Check**:
   - `check-update-ide.yml` (06:00 UTC): Checks for Antigravity IDE updates via `check-version-ide.sh`.
   - `check-update-app.yml` (06:30 UTC): Checks for Antigravity App updates via `check-version-app.sh`.
2. **Auto-Update**: If newer versions are detected, workflows update `antigravity-ide.spec` or
   `antigravity-app.spec`, commit the change, and tag (`ide-vX.Y.Z` or `app-vX.Y.Z`) on `main`.
3. **GitHub → COPR Webhook**: This repo has a native GitHub webhook
   (Settings → Webhooks) pointed at COPR's push endpoint for this package.
   *Any* push to `main` — whether from this workflow's version-bump commit
   or a manual packaging fix — triggers a COPR rebuild automatically.
   There's no custom trigger step to maintain; it's the same mechanism
   COPR uses for any GitHub-tracked SCM package.
4. **COPR Build**: COPR clones this repo, runs `.copr/Makefile` (which
   downloads the real tarballs for x86_64 and aarch64 dynamically for the requested spec),
   and builds the RPM via the corresponding spec file. As part of `%install`, the
   spec also clears `product.json`'s `updateUrl`, disabling the bundled
   in-app updater so it can't produce update notifications that disagree
   with what's actually in the COPR repo (see **Keeping Antigravity Updated**
   above for why).
5. **Published**: The RPM appears in the COPR repo, ready for `sudo dnf
   upgrade` — or fully unattended local installs via
   [`local-autoupdate/`](local-autoupdate/).

**Packaging-only fixes** (no upstream version change, e.g. tweaking
`%install`) don't get picked up by step 1's version comparison, since
nothing upstream changed. For those: bump `Release` by hand, commit, and
push to `main` as usual — the webhook in step 3 rebuilds it regardless of
whether the *version* changed, since it fires on every push.

## 📁 Repository Structure

```
.
├── .copr/
│   └── Makefile                        # Universal COPR SRPM build integration
├── .github/
│   └── workflows/
│       ├── check-update-ide.yml        # Daily version check + auto-update for IDE
│       └── check-update-app.yml        # Daily version check + auto-update for App
├── antigravity-ide.spec                # RPM spec file (IDE)
├── antigravity-ide.desktop             # Desktop launcher entry (IDE)
├── antigravity-ide-url-handler.desktop # URL scheme handler (IDE)
├── antigravity-ide.appdata.xml         # AppStream metadata (IDE)
├── antigravity-ide-wrapper.sh          # CLI wrapper for /usr/bin/antigravity-ide
├── check-version-ide.sh                # IDE version detection utility
├── antigravity-app.spec                # RPM spec file (App)
├── antigravity-app.desktop             # Desktop launcher entry (App)
├── antigravity-app-url-handler.desktop # URL scheme handler (App)
├── antigravity-app.appdata.xml         # AppStream metadata (App)
├── antigravity-app-wrapper.sh          # CLI wrapper for /usr/bin/antigravity-app
├── check-version-app.sh                # App version detection utility
├── local-autoupdate/                   # Optional: auto-install updates on your machine
├── LICENSE                             # MIT (packaging scripts only)
├── README.md                           # This file
└── CONTRIBUTING.md                     # Contribution guide
```

## 📦 What Gets Installed

### Antigravity IDE (`antigravity-ide`)

| Path | Description |
|---|---|
| `/opt/antigravity-ide/` | Main application (upstream binary) |
| `/usr/bin/antigravity-ide` | CLI wrapper script |
| `/usr/share/applications/antigravity-ide.desktop` | Desktop launcher |
| `/usr/share/applications/antigravity-ide-url-handler.desktop` | URL scheme handler |
| `/usr/share/pixmaps/antigravity-ide.png` | Application icon |
| `/usr/share/metainfo/antigravity-ide.appdata.xml` | AppStream metadata |

### Antigravity App (`antigravity-app`)

| Path | Description |
|---|---|
| `/opt/antigravity-app/` | Main application (upstream binary) |
| `/usr/bin/antigravity-app` | CLI wrapper script |
| `/usr/bin/antigravity` | Convenience symlink to `antigravity-app` |
| `/usr/share/applications/antigravity-app.desktop` | Desktop launcher |
| `/usr/share/applications/antigravity-app-url-handler.desktop` | URL scheme handler |
| `/usr/share/pixmaps/antigravity-app.png` | Application icon |
| `/usr/share/metainfo/antigravity-app.appdata.xml` | AppStream metadata |

## 🛠️ Building Locally

If you want to build the RPMs yourself:

```bash
# Install build dependencies
sudo dnf install rpm-build rpmdevtools curl

# Set up rpmbuild tree
rpmdev-setuptree

# --- Option A: Build Antigravity IDE ---
URL_X64=$(grep '^# URL_X64:' antigravity-ide.spec | awk '{print $3}')
URL_ARM64=$(grep '^# URL_ARM64:' antigravity-ide.spec | awk '{print $3}')
curl -sSLf -o ~/rpmbuild/SOURCES/Antigravity-x64.tar.gz "$URL_X64"
curl -sSLf -o ~/rpmbuild/SOURCES/Antigravity-arm64.tar.gz "$URL_ARM64"
cp antigravity-ide.desktop antigravity-ide-url-handler.desktop \
   antigravity-ide.appdata.xml antigravity-ide-wrapper.sh \
   ~/rpmbuild/SOURCES/
rpmbuild -ba antigravity-ide.spec
sudo dnf install ~/rpmbuild/RPMS/x86_64/antigravity-ide-*.rpm

# --- Option B: Build Antigravity App ---
URL_X64=$(grep '^# URL_X64:' antigravity-app.spec | awk '{print $3}')
URL_ARM64=$(grep '^# URL_ARM64:' antigravity-app.spec | awk '{print $3}')
curl -sSLf -o ~/rpmbuild/SOURCES/antigravity-app-x64.tar.gz "$URL_X64"
curl -sSLf -o ~/rpmbuild/SOURCES/antigravity-app-arm64.tar.gz "$URL_ARM64"
cp antigravity-app.desktop antigravity-app-url-handler.desktop \
   antigravity-app.appdata.xml antigravity-app-wrapper.sh \
   ~/rpmbuild/SOURCES/
rpmbuild -ba antigravity-app.spec
sudo dnf install ~/rpmbuild/RPMS/x86_64/antigravity-app-*.rpm
```

## 🤝 Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for details on:

- Reporting issues
- Testing locally
- Submitting pull requests
- Adding support for new Fedora releases

## 📝 Supported Fedora Versions

| Fedora Version | Architecture | Status |
|---|---|---|
| Fedora 43 | x86_64, aarch64 | ✅ Supported |
| Fedora 44 | x86_64, aarch64 | ✅ Supported |
| Fedora 45 | x86_64, aarch64 | ✅ Supported |
| Fedora Rawhide | x86_64, aarch64 | ✅ Supported |

## ⚖️ License

- **Packaging scripts** (this repository): [MIT License](LICENSE)
- **Antigravity Applications**: Proprietary — see [Google's Terms](https://antigravity.google/terms)

The RPM binary is downloaded directly from Google's servers during the build process. This repository does not contain, redistribute, or modify any proprietary Google software.

## 🙏 Acknowledgments

- **Original Project**: Thanks to [Liviu Ionesi](https://github.com/liviuionesi) for creating the original [liviuionesi/antigravity-ide-rpm](https://github.com/liviuionesi/antigravity-ide-rpm) repository, which laid the solid foundation and automation design for this project.
- **Google DeepMind**: For creating Google Antigravity.
- **Fedora COPR**: For providing the excellent community build infrastructure.
