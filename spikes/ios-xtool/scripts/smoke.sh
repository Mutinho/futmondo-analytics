#!/usr/bin/env bash
#
# smoke.sh — Repeatable build/sign/install chain for the xtool iOS spike (B-01).
#
# Wraps the xtool chain into one re-runnable command:
#     xtool dev build  ->  sign  ->  install on the connected device
# then prints a reminder to open the app on the iPhone 13 Pro.
#
# This is the spike's manual acceptance recipe. It is designed to be re-run
# as-is after the ~7-day free-signing validity expires (just re-run it to
# refresh the signature and reinstall).
#
# It fails loudly (set -euo pipefail + explicit prerequisite checks). It stores
# no secret: xtool prompts for your Apple ID interactively when signing.
set -euo pipefail

# ---- helpers --------------------------------------------------------------

log()  { printf '\033[1;34m[smoke]\033[0m %s\n' "$*"; }
warn() { printf '\033[1;33m[smoke][warn]\033[0m %s\n' "$*" >&2; }
die()  { printf '\033[1;31m[smoke][error]\033[0m %s\n' "$*" >&2; exit 1; }

# Resolve the spike root (parent of this scripts/ directory), so the script runs
# correctly regardless of the caller's working directory (idempotent location).
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SPIKE_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

# ---- 1. prerequisites -----------------------------------------------------

command -v xtool >/dev/null 2>&1 || die "'xtool' not found on PATH. Run scripts/setup-wsl.sh and install xtool per its docs."

[ -f "${SPIKE_ROOT}/xtool.yml" ]      || die "xtool.yml not found in ${SPIKE_ROOT}; are you in the spike package?"
[ -f "${SPIKE_ROOT}/Package.swift" ]  || die "Package.swift not found in ${SPIKE_ROOT}; are you in the spike package?"

# Device link check: the iPhone must be attached (usbipd-win) and usbmuxd up.
if command -v idevice_id >/dev/null 2>&1; then
    if [ -z "$(idevice_id -l 2>/dev/null || true)" ]; then
        die "no iOS device detected (idevice_id -l is empty). Attach the iPhone via usbipd-win and ensure usbmuxd is running."
    fi
    log "device link OK: $(idevice_id -l | tr '\n' ' ')"
else
    warn "idevice_id not found; skipping the device-presence check. If install fails, run setup-wsl.sh first."
fi

# ---- 2. build / sign / install -------------------------------------------
#
# 'xtool dev build' builds, signs (free Apple ID, interactive) and installs the
# app onto the attached device in one step. If the installed xtool splits these
# into separate subcommands, adjust here; the chain's intent is build->sign->install.

cd "${SPIKE_ROOT}"

log "running: xtool dev build (build -> sign -> install)"
if ! xtool dev build; then
    die "xtool dev build failed. Common causes: signing expired (re-run this script), device not attached, or Apple ID sign-in required."
fi

# ---- 3. manual smoke reminder --------------------------------------------

cat <<'EOF'

------------------------------------------------------------------------------
Manual smoke step (the real acceptance of the spike):
------------------------------------------------------------------------------
  1. On the iPhone 13 Pro, find the "XToolSpike" app icon.
  2. First launch of a free-signed app: go to
        Settings > General > VPN & Device Management
     and TRUST the developer certificate (your Apple ID).
  3. Open the app. Success = it shows the screen "xtool OK" + the version.
  4. Record the result (and a screenshot) under "## Hallazgos" in
     docs/spikes/ios-xtool.md. Note any blocker under "## Bloqueos observados".

Signing validity is ~7 days on a free account: re-run this same script to
refresh the signature and reinstall.
------------------------------------------------------------------------------

EOF

log "smoke chain finished. Open the app on the device to confirm boot."
