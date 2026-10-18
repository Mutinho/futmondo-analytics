#!/usr/bin/env bash
#
# install-app.sh — Recurring install of the Futmondo native iOS app (F1) onto
# the iPhone, from WSL.
#
# Run this (from WSL) every time you want to (re)install and launch the app.
# It mirrors spikes/ios-xtool/scripts/install-app.sh but targets THIS project
# (the `ios/` SwiftPM package: product `FutmondoApp`, bundleID
# `com.futmondo.app`) instead of the throwaway spike app.
#
# What it does:
#   1. Puts the xtool AppImage and the Swift 6.4.0 toolchain on PATH.
#   2. Recomputes the WSL default-gateway IP (it changes across WSL restarts)
#      and points xtool at the Apple usbmuxd relayed from Windows on TCP 27015
#      via USBMUXD_SOCKET_ADDRESS.
#   3. Verifies the device is visible, then runs `xtool dev run` from `ios/`
#      (build -> sign -> package -> install -> launch).
#
# PREREQUISITES (one-time, see spikes/ios-xtool runbook / docs):
#   - Windows side prepared (portproxy 27015 + firewall) and Apple Devices
#     seeing the iPhone.
#   - `xtool setup` already done (login + Darwin SDK with Swift 6.4.0).
#
# Free-signing validity is ~7 days (B-09, deferred): just re-run this script to
# refresh+reinstall. It fails loudly (set -euo pipefail) and stores no credential.
set -euo pipefail

log()  { printf '\033[1;34m[install-app]\033[0m %s\n' "$*"; }
warn() { printf '\033[1;33m[install-app][warn]\033[0m %s\n' "$*" >&2; }
die()  { printf '\033[1;31m[install-app][error]\033[0m %s\n' "$*" >&2; exit 1; }

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
IOS_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"   # the ios/ package root (has Package.swift + xtool.yml)

[ -f "${IOS_ROOT}/xtool.yml" ] || die "No xtool.yml found in ${IOS_ROOT}. Run from the ios/ project."

# --- 1. PATH: xtool (AppImage) + Swift 6.4.0 toolchain --------------------
# Prefer the 6.4.0 toolchain (matches the Xcode 27 SDK). Fall back to ~/.swift
# with a warning: 6.0.3 will not build the Darwin SDK.
XTOOL_BIN="${HOME}/.local/bin"
if [ -x "${HOME}/.swift640/usr/bin/swiftc" ]; then
    SWIFT_BIN="${HOME}/.swift640/usr/bin"
elif [ -x "${HOME}/.swift/usr/bin/swiftc" ]; then
    SWIFT_BIN="${HOME}/.swift/usr/bin"
    warn "Using ~/.swift (not ~/.swift640). If the build fails with 'this SDK is"
    warn "not supported by the compiler', install Swift 6.4.0 into ~/.swift640."
else
    die "No Swift toolchain found in ~/.swift640 or ~/.swift."
fi
export PATH="${XTOOL_BIN}:${SWIFT_BIN}:${PATH}"

command -v xtool >/dev/null 2>&1 || die "'xtool' not found in ${XTOOL_BIN}. Install the xtool AppImage (see runbook)."

# --- 2. Relay address: WSL gateway IP : 27015 -----------------------------
GATEWAY="$(ip route show default 2>/dev/null | awk '{print $3; exit}')"
[ -n "${GATEWAY}" ] || die "Could not determine the WSL default gateway IP."
export USBMUXD_SOCKET_ADDRESS="${GATEWAY}:27015"
log "Using Apple usbmuxd relay at ${USBMUXD_SOCKET_ADDRESS} (Windows side)."

# --- 3. Verify device reachability via the relay --------------------------
log "Checking that xtool sees the device..."
if ! xtool devices 2>/dev/null | grep -v -i 'libxml2' | grep -q '\[usb\]'; then
    die "xtool does not see the iPhone. Checklist:
  - iPhone connected and UNLOCKED, 'Trust this computer' accepted.
  - Apple Devices (Windows) shows the iPhone.
  - Windows portproxy 27015 active.
  - TCP ${GATEWAY}:27015 reachable from WSL."
fi
log "Device OK: $(xtool devices 2>/dev/null | grep -v -i 'libxml2' | head -1)"

# --- 4. Build + sign + install + launch (from ios/) -----------------------
cd "${IOS_ROOT}"
log "Running: xtool dev run  (product FutmondoApp, bundleID com.futmondo.app)"
log "If 'Provisioning' fails with a 'Connection reset by peer' talking to"
log "api.appstoreconnect.apple.com, it is an Apple-API/network hiccup (not the"
log "app): re-run this script; check 'date' in WSL and the 27015 relay."
xtool dev run

cat <<'EOF'

------------------------------------------------------------------------------
First launch after a (re)signing: on the iPhone go to
  Settings > General > VPN & Device Management > (your Apple ID) > Trust
then open "Futmondo". Validate the F1 flow: login -> auto-login on relaunch ->
logout. The refresh token lives in the iOS Keychain; the access token stays in
memory.

Free-signing validity is ~7 days: re-run this script to refresh+reinstall.
------------------------------------------------------------------------------
EOF
