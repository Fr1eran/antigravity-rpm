# Contributing to Antigravity RPM Packaging

First off, thank you for considering contributing to this community project! It's people like you that make the open-source and Fedora communities such a great place.

## Scope of This Project

Please note: **This repository only contains the packaging scripts for Fedora.**

- If you have an issue with the packaging itself (e.g., installation fails, desktop entry is missing, CLI wrapper is broken), you are in the right place! Please [open an issue](https://github.com/Fr1eran/antigravity-rpm/issues).
- If you have an issue with the Antigravity application itself (e.g., a bug in the code editor, an agent feature not working), please report it to Google directly. We cannot fix bugs in the proprietary binary.

## How the Automation Works

This project is highly automated:

1. GitHub Actions workflows (`.github/workflows/check-update-ide.yml` and `check-update-app.yml`) run daily.
2. They detect the latest version and binary URLs for Antigravity IDE and Antigravity App.
3. If a new version is found, the workflow automatically updates the respective `.spec` file, commits the change, and tags it (`ide-vX.Y.Z` or `app-vX.Y.Z`).
4. Pushing to `main` triggers the webhook to Fedora COPR.
5. COPR pulls the repository, executes `.copr/Makefile` to download the appropriate tarball, and builds the `.rpm`.

## Testing Changes Locally

If you want to modify the `.spec` files or desktop integration files, you should build the RPM locally to test it.

### Prerequisites

You need standard RPM build tools:

```bash
sudo dnf install rpm-build rpmdevtools curl spectool
```

### Build Workflow

1. Clone this repository:
   ```bash
   git clone https://github.com/Fr1eran/antigravity-rpm.git
   cd antigravity-rpm
   ```

2. Set up your local RPM build tree:
   ```bash
   rpmdev-setuptree
   ```

3. Download upstream tarballs (both x86_64 and aarch64) to your SOURCES directory:
   - For **Antigravity IDE**:
     ```bash
     URL_X64=$(grep '^# URL_X64:' antigravity-ide.spec | awk '{print $3}')
     URL_ARM64=$(grep '^# URL_ARM64:' antigravity-ide.spec | awk '{print $3}')
     curl -sSLf -o ~/rpmbuild/SOURCES/Antigravity-x64.tar.gz "$URL_X64"
     curl -sSLf -o ~/rpmbuild/SOURCES/Antigravity-arm64.tar.gz "$URL_ARM64"
     ```
   - For **Antigravity App**:
     ```bash
     URL_X64=$(grep '^# URL_X64:' antigravity-app.spec | awk '{print $3}')
     URL_ARM64=$(grep '^# URL_ARM64:' antigravity-app.spec | awk '{print $3}')
     curl -sSLf -o ~/rpmbuild/SOURCES/antigravity-app-x64.tar.gz "$URL_X64"
     curl -sSLf -o ~/rpmbuild/SOURCES/antigravity-app-arm64.tar.gz "$URL_ARM64"
     ```

4. Copy the local integration files to SOURCES:
   - For **Antigravity IDE**:
     ```bash
     cp antigravity-ide.desktop antigravity-ide-url-handler.desktop \
        antigravity-ide.appdata.xml antigravity-ide-wrapper.sh \
        ~/rpmbuild/SOURCES/
     ```
   - For **Antigravity App**:
     ```bash
     cp antigravity-app.desktop antigravity-app-url-handler.desktop \
        antigravity-app.appdata.xml antigravity-app-wrapper.sh \
        ~/rpmbuild/SOURCES/
     ```

5. Build the RPM:
   ```bash
   # Build Antigravity IDE
   rpmbuild -ba antigravity-ide.spec

   # Or build Antigravity App
   rpmbuild -ba antigravity-app.spec
   ```

6. Install and test your newly built RPM:
   ```bash
   sudo dnf install ~/rpmbuild/RPMS/x86_64/antigravity-*.rpm
   ```

## Pull Requests

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-fix`)
3. Commit your changes (`git commit -m 'feat: add amazing fix'`)
4. Push to the branch (`git push origin feature/amazing-fix`)
5. Open a Pull Request

## Adding Support for New Fedora Versions

When a new Fedora version is released (or enters beta), you don't need to change any code here. The repository maintainer simply needs to go to the [COPR project settings](https://copr.fedorainfracloud.org/coprs/fr1eran/antigravity-rpm/edit/) and check the box for the new target chroots (e.g., `fedora-45-x86_64` and `fedora-45-aarch64`).
