#!/bin/bash
# ============================================================================
# check-version-ide.sh — Detect the latest Antigravity IDE version and URLs
# ============================================================================

set -euo pipefail

API_URL="${ANTIGRAVITY_IDE_API_URL:-https://antigravity-ide-auto-updater-974169037036.us-central1.run.app/releases}"
DOWNLOAD_PAGE="https://antigravity.google/download"

NEW_VERSION=""
URL_X64=""
URL_ARM64=""

# Strategy 1: Query the Antigravity IDE auto-updater releases API
RELEASES_JSON=$(curl -sL --compressed "$API_URL" 2>/dev/null || true)
if [[ -n "$RELEASES_JSON" ]]; then
    RELEASE_DATA=$(python3 -c "
import json, sys
try:
    data = json.loads(sys.argv[1])
    first = data[0] if isinstance(data, list) else data.get('versions', [])[0]
    print(first.get('version', ''), first.get('execution_id', ''))
except Exception:
    pass
" "$RELEASES_JSON" 2>/dev/null || true)

    if [[ -n "$RELEASE_DATA" ]]; then
        VERSION_CANDIDATE=$(echo "$RELEASE_DATA" | awk '{print $1}')
        EXEC_ID=$(echo "$RELEASE_DATA" | awk '{print $2}')
        if [[ -n "$VERSION_CANDIDATE" && -n "$EXEC_ID" ]]; then
            BASE_URL="https://edgedl.me.gvt1.com/edgedl/release2/j0qc3/antigravity/stable/${VERSION_CANDIDATE}-${EXEC_ID}"
            URL_X64_TEST="${BASE_URL}/linux-x64/Antigravity%20IDE.tar.gz"
            URL_ARM64_TEST="${BASE_URL}/linux-arm/Antigravity%20IDE.tar.gz"
            # Verify the tarball actually exists at this endpoint before using it
            if curl --head --silent --fail "$URL_X64_TEST" >/dev/null 2>&1; then
                NEW_VERSION="$VERSION_CANDIDATE"
                URL_X64="$URL_X64_TEST"
                URL_ARM64="$URL_ARM64_TEST"
            fi
        fi
    fi
fi

# Strategy 2: Fallback to scraping the download page
if [[ -z "$NEW_VERSION" || -z "$URL_X64" || -z "$URL_ARM64" ]]; then
    PAGE_CONTENT=$(curl -sL --compressed "$DOWNLOAD_PAGE" 2>/dev/null || true)
    URL_X64=$(echo "$PAGE_CONTENT" | grep -oP 'href="[^"]*linux-x64[^"]*tar\.gz[^"]*"' | grep -i "IDE" | head -1 | cut -d'"' -f2 || true)
    URL_ARM64=$(echo "$PAGE_CONTENT" | grep -oP 'href="[^"]*linux-arm[^"]*tar\.gz[^"]*"' | grep -i "IDE" | head -1 | cut -d'"' -f2 || true)
    if [[ -n "$URL_X64" ]]; then
        NEW_VERSION=$(echo "$URL_X64" | grep -oP '\d+\.\d+\.\d+' | head -1 || true)
    fi
fi

if [[ -z "$NEW_VERSION" || -z "$URL_X64" || -z "$URL_ARM64" ]]; then
    echo "ERROR: Could not detect latest Antigravity IDE version and URLs" >&2
    exit 1
fi

echo "version=$NEW_VERSION"
echo "url_x64=$URL_X64"
echo "url_arm64=$URL_ARM64"
