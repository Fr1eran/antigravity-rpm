# ============================================================================
# antigravity-ide.spec — Fedora RPM spec for Google Antigravity IDE
# ============================================================================
# This is an unofficial community package. Antigravity IDE is proprietary
# software developed by Google. This spec file simply repackages the upstream
# pre-built Linux tarball for convenient installation via DNF.
# ============================================================================

%global debug_package   %{nil}
%global __strip         /bin/true
%global _build_id_links none

# Upstream tarball extracts to "Antigravity-x64/" (or "Antigravity-arm64/")
%global upstream_name   Antigravity
%global install_dir     /opt/%{name}

Name:           antigravity-ide
Version:        2.6.0
Release:        1%{?dist}
Summary:        Google Antigravity IDE — An agentic AI development platform
License:        LicenseRef-Google-Antigravity
URL:            https://antigravity.google/

# The tarballs are downloaded at build time via the .copr/Makefile
# URL_X64:        https://edgedl.me.gvt1.com/edgedl/release2/j0qc3/antigravity/stable/2.6.0-5526304964083712/linux-x64/Antigravity%20IDE.tar.gz
# URL_ARM64:      https://edgedl.me.gvt1.com/edgedl/release2/j0qc3/antigravity/stable/2.6.0-5526304964083712/linux-arm/Antigravity%20IDE.tar.gz
Source0:        Antigravity-x64.tar.gz
Source1:        Antigravity-arm64.tar.gz

# Desktop and system integration files (shipped in this repo)
Source2:        antigravity-ide.desktop
Source3:        antigravity-ide-url-handler.desktop
Source4:        antigravity-ide.appdata.xml
Source5:        antigravity-ide-wrapper.sh

ExclusiveArch:  x86_64 aarch64

# ---- Build dependencies ----
# python3 is used at install time to disable the bundled Electron
# auto-updater (see %install) via an in-place JSON edit of product.json.
BuildRequires:  python3

# ---- Disable automatic dependency scanning ----
# The upstream binary bundles its own Electron/Chromium/Node.js runtime.
# Scanning it would generate hundreds of false requires/provides and
# potentially conflict with system libraries.
AutoReqProv:    no

# ---- Runtime dependencies ----
# These are the system libraries the bundled Chromium expects to dlopen().
Requires:       alsa-lib
Requires:       at-spi2-core
Requires:       bash
Requires:       cairo
Requires:       cups-libs
Requires:       curl
Requires:       dbus-libs
Requires:       expat
Requires:       glib2
Requires:       glibc
Requires:       gtk3
Requires:       libgcc
Requires:       libX11
Requires:       libXcomposite
Requires:       libXdamage
Requires:       libXext
Requires:       libXfixes
Requires:       libXrandr
Requires:       libxcb
Requires:       libxkbcommon
Requires:       libxkbfile
Requires:       libsecret
Requires:       libsoup3
Requires:       libstdc++
Requires:       mesa-libgbm
Requires:       nspr
Requires:       nss
Requires:       openssl
Requires:       pango
Requires:       systemd-libs
Requires:       webkit2gtk4.1

%description
Google Antigravity IDE is an agentic AI development platform from Google,
evolving the IDE into the agent-first era.

This is an UNOFFICIAL community package for Fedora. It repackages the
upstream prebuilt Linux release under /opt/antigravity-ide and provides
a command-line wrapper and desktop entries.

# ============================================================================
%prep
# Extract into a clean directory regardless of the tarball's internal structure
%setup -q -c -T -n %{name}-%{version}

%ifarch x86_64
tar xzf %{SOURCE0} --strip-components=1
%endif

%ifarch aarch64
tar xzf %{SOURCE1} --strip-components=1
%endif

# ============================================================================
%install
# Install the IDE to /opt/antigravity-ide/
mkdir -p %{buildroot}%{install_dir}
cp -a . %{buildroot}%{install_dir}/

# Rename the upstream binary "antigravity" → "antigravity-ide" inside /opt
# to match the package name and avoid PATH conflicts.
if [ -f %{buildroot}%{install_dir}/antigravity ] && \
   [ ! -f %{buildroot}%{install_dir}/antigravity-ide ]; then
    mv %{buildroot}%{install_dir}/antigravity \
       %{buildroot}%{install_dir}/antigravity-ide
fi

# Disable the bundled Electron auto-updater. Updates for this package are
# managed via dnf/COPR (see .github/workflows/check-update-ide.yml), not the
# app's own updater — leaving updateUrl pointed at a live endpoint causes
# spurious "update available" notifications inside the IDE that don't
# correspond to real dnf updates and can reference unrelated release notes.
PRODUCT_JSON="%{buildroot}%{install_dir}/resources/app/product.json"
if [ -f "$PRODUCT_JSON" ]; then
    python3 - "$PRODUCT_JSON" <<'PYEOF'
import json
import sys

path = sys.argv[1]
with open(path) as f:
    data = json.load(f)
data["updateUrl"] = ""
with open(path, "w") as f:
    json.dump(data, f, indent="\t")
    f.write("\n")
PYEOF
fi

# Install the CLI wrapper script to /usr/bin/
mkdir -p %{buildroot}%{_bindir}
install -m 755 %{SOURCE5} %{buildroot}%{_bindir}/antigravity-ide

# Desktop entries
mkdir -p %{buildroot}%{_datadir}/applications
install -m 644 %{SOURCE2} %{buildroot}%{_datadir}/applications/
install -m 644 %{SOURCE3} %{buildroot}%{_datadir}/applications/

# AppStream metadata
mkdir -p %{buildroot}%{_datadir}/metainfo
install -m 644 %{SOURCE4} %{buildroot}%{_datadir}/metainfo/

# Icon (extract from upstream resources if available)
mkdir -p %{buildroot}%{_datadir}/pixmaps
if [ -f %{buildroot}%{install_dir}/resources/app/resources/linux/code.png ]; then
    cp %{buildroot}%{install_dir}/resources/app/resources/linux/code.png \
       %{buildroot}%{_datadir}/pixmaps/antigravity-ide.png
fi

# Shell completions (if upstream provides them)
if [ -d %{buildroot}%{install_dir}/resources/completions ]; then
    mkdir -p %{buildroot}%{_datadir}/bash-completion/completions
    cp %{buildroot}%{install_dir}/resources/completions/bash/antigravity-ide \
       %{buildroot}%{_datadir}/bash-completion/completions/ 2>/dev/null || true
    mkdir -p %{buildroot}%{_datadir}/zsh/site-functions
    cp %{buildroot}%{install_dir}/resources/completions/zsh/_antigravity-ide \
       %{buildroot}%{_datadir}/zsh/site-functions/ 2>/dev/null || true
fi

# Ensure the chrome-sandbox has the correct permissions (SUID)
chmod 4755 %{buildroot}%{install_dir}/chrome-sandbox 2>/dev/null || true

# ============================================================================
%files
%{install_dir}/
%{_bindir}/antigravity-ide
%{_datadir}/applications/antigravity-ide.desktop
%{_datadir}/applications/antigravity-ide-url-handler.desktop
%{_datadir}/metainfo/antigravity-ide.appdata.xml
%{_datadir}/pixmaps/antigravity-ide.png
%dir %{_datadir}/bash-completion
%dir %{_datadir}/bash-completion/completions
%{_datadir}/bash-completion/completions/antigravity-ide
%dir %{_datadir}/zsh
%dir %{_datadir}/zsh/site-functions
%{_datadir}/zsh/site-functions/_antigravity-ide

# ============================================================================
%changelog
* Tue Oct 27 2026 Automated Update <antigravity-ide-rpm@users.noreply.github.com> - 2.6.0-1
- Update to upstream version 2.6.0
* Fri Aug 14 2026 Automated Update <antigravity-ide-rpm@users.noreply.github.com> - 2.5.5-1
- Update to upstream version 2.5.5
* Thu Aug 13 2026 Automated Update <antigravity-ide-rpm@users.noreply.github.com> - 2.5.2-1
- Update to upstream version 2.5.2
* Tue Jul 28 2026 Community Maintainer <antigravity-ide-rpm@users.noreply.github.com> - 2.1.1-2
- Clear product.json's updateUrl at install time to disable the bundled
  in-app auto-updater, which was showing spurious "update available"
  notifications (pointing at unrelated upstream VS Code release notes)
  even on fully up-to-date dnf installs. Updates are managed via dnf/COPR.
* Thu Jul 23 2026 Community Maintainer <antigravity-ide-rpm@users.noreply.github.com> - 2.1.1-1
- Initial community RPM package for Fedora
- Repackages upstream tar.gz from antigravity.google
