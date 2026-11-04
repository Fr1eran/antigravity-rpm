# ============================================================================
# antigravity-app.spec — Fedora RPM spec for Google Antigravity App
# ============================================================================
# This is an unofficial community package. Antigravity is proprietary
# software developed by Google. This spec file simply repackages the upstream
# pre-built Linux tarball for convenient installation via DNF.
# ============================================================================

%global debug_package   %{nil}
%global __strip         /bin/true
%global _build_id_links none

%global install_dir     /opt/%{name}

Name:           antigravity-app
Version:        2.29.0
Release:        1%{?dist}
Summary:        Google Antigravity App — Agent orchestration platform
License:        LicenseRef-Google-Antigravity
URL:            https://antigravity.google/

# The tarballs are downloaded at build time via the .copr/Makefile
# URL_X64:        https://storage.googleapis.com/antigravity-public/antigravity-hub/2.29.0-5723181030440960/linux-x64/Antigravity.tar.gz
# URL_ARM64:      https://storage.googleapis.com/antigravity-public/antigravity-hub/2.29.0-5723181030440960/linux-arm/Antigravity.tar.gz
Source0:        antigravity-app-x64.tar.gz
Source1:        antigravity-app-arm64.tar.gz

# Desktop and system integration files (shipped in this repo)
Source2:        antigravity-app.desktop
Source3:        antigravity-app-url-handler.desktop
Source4:        antigravity-app.appdata.xml
Source5:        antigravity-app-wrapper.sh

Provides:       antigravity = %{version}-%{release}
ExclusiveArch:  x86_64 aarch64

# ---- Build dependencies ----
BuildRequires:  python3

# ---- Disable automatic dependency scanning ----
# The upstream binary bundles its own Electron/Chromium/Node.js runtime.
AutoReqProv:    no

# ---- Runtime dependencies ----
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
Google Antigravity App is an agentic AI development platform from Google,
orchestrating intelligent agents across your machine independently of an IDE.

This is an UNOFFICIAL community package for Fedora. It repackages the
upstream prebuilt Linux release under /opt/antigravity-app and provides
a command-line wrapper and desktop entries.

# ============================================================================
%prep
%setup -q -c -T -n %{name}-%{version}

%ifarch x86_64
tar xzf %{SOURCE0} --strip-components=1
%endif

%ifarch aarch64
tar xzf %{SOURCE1} --strip-components=1
%endif

# ============================================================================
%install
mkdir -p %{buildroot}%{install_dir}
cp -a . %{buildroot}%{install_dir}/

# Standardize binary name inside /opt/antigravity-app
if [ -f %{buildroot}%{install_dir}/antigravity ] && \
   [ ! -f %{buildroot}%{install_dir}/Antigravity ]; then
    ln -sf antigravity %{buildroot}%{install_dir}/Antigravity
fi

# Disable bundled Electron auto-updater if product.json is present
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

# Install CLI wrapper script and symlinks
mkdir -p %{buildroot}%{_bindir}
install -m 755 %{SOURCE5} %{buildroot}%{_bindir}/antigravity-app
ln -sf antigravity-app %{buildroot}%{_bindir}/antigravity

# Desktop entries
mkdir -p %{buildroot}%{_datadir}/applications
install -m 644 %{SOURCE2} %{buildroot}%{_datadir}/applications/
install -m 644 %{SOURCE3} %{buildroot}%{_datadir}/applications/

# AppStream metadata
mkdir -p %{buildroot}%{_datadir}/metainfo
install -m 644 %{SOURCE4} %{buildroot}%{_datadir}/metainfo/

# Icon (extract from upstream resources if available)
mkdir -p %{buildroot}%{_datadir}/pixmaps
ICON_SRC=$(find %{buildroot}%{install_dir} -name "code.png" -o -name "icon.png" -o -name "antigravity.png" | head -n 1)
if [ -n "$ICON_SRC" ]; then
    cp "$ICON_SRC" %{buildroot}%{_datadir}/pixmaps/antigravity-app.png
else
    # Fallback to a valid minimal PNG if upstream structure changes
    printf '\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15c4\x00\x00\x00\rIDATx\x9cc`\x00\x00\x00\x02\x00\x01H\xaf\xa4q\x00\x00\x00\x00IEND\xaeB`\x82' > %{buildroot}%{_datadir}/pixmaps/antigravity-app.png
fi

# Ensure chrome-sandbox permissions (SUID)
chmod 4755 %{buildroot}%{install_dir}/chrome-sandbox 2>/dev/null || true

# ============================================================================
%files
%{install_dir}/
%{_bindir}/antigravity-app
%{_bindir}/antigravity
%{_datadir}/applications/antigravity-app.desktop
%{_datadir}/applications/antigravity-app-url-handler.desktop
%{_datadir}/metainfo/antigravity-app.appdata.xml
%{_datadir}/pixmaps/antigravity-app.png

# ============================================================================
%changelog
* Wed Nov 04 2026 Automated Update <antigravity-rpm@users.noreply.github.com> - 2.29.0-1
- Update to upstream version 2.29.0
- Initial community RPM package for Antigravity App
