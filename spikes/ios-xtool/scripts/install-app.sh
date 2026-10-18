#!/usr/bin/env bash
#
# install-app.sh — Recurring install of the xtool spike app onto the iPhone.
#
# Run this (from WSL) every time you want to (re)install and launch the app.
# It automates the recurring friction documented in docs/spikes/ios-xtool.md:
#   1. Puts the xtool AppImage and the Swift 6.4.0 toolchain on PATH.
#   2. Recomputes the WSL default-gateway IP (it changes across WSL restarts)
#      and points xtool at the Apple usbmuxd relayed from Windows on TCP 27015
#      via USBMUXD_SOCKET_ADDRESS.
#   3. Starts the local usbmuxd if it is not running (harmless with the relay).
#   4. Verifies the device is visible, then runs `xtool dev run`
#      (build -> sign -> package -> install -> launch).
#
# PREREQUISITES (one-time, see the runbook):
#   - Windows side prepared with scripts/windows-prepare.ps1 (portproxy 27015 +
#     firewall) and Apple Devices seeing the iPhone.
#   - `xtool setup` already done (login + Darwin SDK installed with Swift 6.4.0).
#
# It fails loudly (set -euo pipefail) and stores no credential.
set -euo pipefail

log()  { printf '\033[1;34m[install-app]\033[0m %s\n' "$*"; }
warn() { printf '\033[1;33m[install-app][warn]\033[0m %s\n' "$*" >&2; }
die()  { printf '\033[1;31m[install-app][error]\033[0m %s\n' "$*" >&2; exit 1; }

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SPIKE_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

# --- 1. PATH: xtool (AppImage) + Swift 6.4.0 toolchain --------------------
# Prefer the 6.4.0 toolchain (matches the Xcode 27 SDK). Fall back to ~/.swift
# if ~/.swift640 is absent, but warn: 6.0.3 will not build the SDK.
XTOOL_BIN="${HOME}/.local/bin"
if [ -x "${HOME}/.swift640/usr/bin/swiftc" ]; then
    SWIFT_BIN="${HOME}/.swift640/usr/bin"
elif [ -x "${HOME}/.swift/usr/bin/swiftc" ]; then
    SWIFT_BIN="${HOME}/.swift/usr/bin"
    warn "Using ~/.swift (not ~/.swift640). If the build fails with 'this SDK is"
    warn "not supported by the compiler', install Swift 6.4.0 into ~/.swift640."
else
    die "No Swift toolchain found in ~/.swift640 or ~/.swift. Run setup-wsl.sh first."
fi
export PATH="${XTOOL_BIN}:${SWIFT_BIN}:${PATH}"

command -v xtool >/dev/null 2>&1 || die "'xtool' not found in ${XTOOL_BIN}. Install the xtool AppImage (see runbook)."

# --- 2. Relay address: WSL gateway IP : 27015 -----------------------------
GATEWAY="$(ip route show default 2>/dev/null | awk '{print $3; exit}')"
[ -n "${GATEWAY}" ] || die "Could not determine the WSL default gateway IP."
export USBMUXD_SOCKET_ADDRESS="${GATEWAY}:27015"
log "Using Apple usbmuxd relay at ${USBMUXD_SOCKET_ADDRESS} (Windows side)."

# --- 3. Local usbmuxd: NOT needed on the relay path ----------------------
# With USBMUXD_SOCKET_ADDRESS pointing at the Apple usbmuxd on Windows, the
# local Linux usbmuxd is irrelevant. We intentionally do NOT start it (that
# would need sudo and is unrelated to the relay path).

# --- 4. Verify device reachability via the relay --------------------------
log "Checking that xtool sees the device..."
if ! xtool devices 2>/dev/null | grep -v -i 'libxml2' | grep -q '\[usb\]'; then
    die "xtool does not see the iPhone. Checklist:
  - iPhone connected and UNLOCKED, 'Trust this computer' accepted.
  - Apple Devices (Windows) shows the iPhone.
  - Windows portproxy 27015 active (run scripts/windows-prepare.ps1 as admin).
  - TCP ${GATEWAY}:27015 reachable from WSL."
fi
log "Device OK: $(xtool devices 2>/dev/null | grep -v -i 'libxml2' | head -1)"

# --- 5. Build + sign + install + launch -----------------------------------
cd "${SPIKE_ROOT}"
log "Running: xtool dev run (build -> sign -> install -> launch)"
xtool dev run

cat <<'EOF'

------------------------------------------------------------------------------
If this is the first launch after a (re)signing, on the iPhone go to
  Settings > General > VPN & Device Management > (your Apple ID) > Trust
then open "XToolSpike". Success = it shows "xtool OK" + the version.

Free-signing validity is ~7 days: just re-run this script to refresh+reinstall.
------------------------------------------------------------------------------
EOF
