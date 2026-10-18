#!/usr/bin/env bash
#
# setup-wsl.sh — Idempotent environment setup for the xtool iOS spike (B-01).
#
# Prepares an Ubuntu/WSL environment to build and install an iOS app with xtool
# against a physical device (iPhone 13 Pro) over USB/IP.
#
# What it does (all idempotent — safe to re-run):
#   1. Detect the Ubuntu version.
#   2. Install the Swift toolchain, with a documented fallback for Ubuntu 26.04
#      where no official Swift binary exists yet (risk R-02).
#   3. Install usbmuxd / libimobiledevice (the Linux side of the USB device link).
#   4. Print the Windows-side notes for usbipd-win (installed on the HOST, not
#      inside WSL) and for xtool itself.
#
# It fails loudly (set -euo pipefail + explicit checks). It NEVER hardcodes an
# Apple credential or any secret — signing uses your own Apple ID entered
# interactively by xtool at build/sign time.
set -euo pipefail

# ---- helpers --------------------------------------------------------------

log()  { printf '\033[1;34m[setup]\033[0m %s\n' "$*"; }
warn() { printf '\033[1;33m[setup][warn]\033[0m %s\n' "$*" >&2; }
die()  { printf '\033[1;31m[setup][error]\033[0m %s\n' "$*" >&2; exit 1; }

require_cmd() {
    # Fail loudly if a hard prerequisite command is missing.
    local cmd="$1" hint="${2:-}"
    if ! command -v "$cmd" >/dev/null 2>&1; then
        die "required command '$cmd' not found.${hint:+ $hint}"
    fi
}

# ---- 0. sanity ------------------------------------------------------------

[ "$(id -u)" -ne 0 ] || warn "running as root; the script uses sudo itself, prefer a normal user."
require_cmd sudo "Install sudo or run on a WSL distro that provides it."
require_cmd apt-get "This script targets Debian/Ubuntu (apt). Other distros are unsupported."

# ---- 1. detect Ubuntu version --------------------------------------------

if [ ! -r /etc/os-release ]; then
    die "/etc/os-release not readable; cannot detect the distribution."
fi
# shellcheck disable=SC1091
. /etc/os-release
UBUNTU_ID="${ID:-unknown}"
UBUNTU_VERSION="${VERSION_ID:-unknown}"
log "detected distribution: ${UBUNTU_ID} ${UBUNTU_VERSION}"

if [ "$UBUNTU_ID" != "ubuntu" ]; then
    warn "distribution is not Ubuntu; the Swift install path may differ."
fi

# ---- 2. Swift toolchain ---------------------------------------------------
#
# Official Swift.org binaries are published for Ubuntu 22.04 and 24.04. On
# Ubuntu 26.04 (the live environment) there is no matching tarball yet
# (risk R-02). Preferred install path is 'swiftly' (the official toolchain
# manager, version-agnostic); if swiftly cannot resolve a toolchain for this
# release, fall back to pinning the 24.04-tagged toolchain, which runs on 26.04
# in practice.

install_swift() {
    if command -v swift >/dev/null 2>&1; then
        log "swift already present: $(swift --version 2>&1 | head -n1)"
        return 0
    fi

    log "installing Swift build prerequisites via apt..."
    sudo apt-get update -y
    # Minimal set required by the Swift toolchain on Ubuntu.
    # NOTE (Ubuntu 26.04 / R-02): the 24.04-tagged toolchain links against the
    # non-wide libncurses.so.6, which 26.04 no longer ships by default (it ships
    # libncursesw6). Install libncurses6 explicitly so the toolchain loads.
    sudo apt-get install -y \
        binutils git gnupg2 libc6-dev libcurl4-openssl-dev libedit2 \
        libgcc-s1 libncurses6 libpython3-dev libsqlite3-0 libstdc++6 libxml2-dev \
        libz3-dev pkg-config tzdata unzip zlib1g-dev curl ca-certificates

    # --- Preferred: swiftly (official toolchain manager) -------------------
    log "attempting Swift install via swiftly (preferred, version-agnostic)..."
    if curl -fsSL https://swiftlang.github.io/swiftly/swiftly-install.sh -o /tmp/swiftly-install.sh; then
        if bash /tmp/swiftly-install.sh -y; then
            # swiftly installs into ~/.local/share/swiftly; load its env.
            # shellcheck disable=SC1090
            [ -r "${HOME}/.local/share/swiftly/env.sh" ] && . "${HOME}/.local/share/swiftly/env.sh"
            if command -v swiftly >/dev/null 2>&1; then
                swiftly install latest || warn "swiftly could not install 'latest' automatically."
                swiftly use latest || true
            fi
        else
            warn "swiftly installer returned non-zero; will try the tagged-toolchain fallback."
        fi
    else
        warn "could not download swiftly installer; will try the tagged-toolchain fallback."
    fi

    if command -v swift >/dev/null 2>&1; then
        log "swift installed via swiftly: $(swift --version 2>&1 | head -n1)"
        return 0
    fi

    # --- Fallback: 24.04-tagged official toolchain -------------------------
    # On Ubuntu 26.04 there is no native tarball; the 24.04 build is the closest
    # ABI match and works in practice. Pin the URL to the 24.04 artifact.
    warn "falling back to the Ubuntu 24.04-tagged Swift toolchain (R-02: no 26.04 binary)."
    # The SDK extracted from Xcode 27 is built with Swift 6.4, so the compiler
    # MUST be 6.4.x (a 6.0.x toolchain fails with "this SDK is not supported by
    # the compiler"). Swift.org has no Ubuntu 26.04 binary, so we pin the
    # 24.04-tagged 6.4.1 release, which runs on 26.04 with the compat shims above.
    local swift_version="6.4.1"
    local swift_release="swift-${swift_version}-RELEASE"
    local swift_tarball="${swift_release}-ubuntu24.04.tar.gz"
    local swift_url="https://download.swift.org/swift-${swift_version}-release/ubuntu2404/${swift_release}/${swift_tarball}"
    local install_root="${HOME}/.swift"

    mkdir -p "$install_root"
    log "downloading ${swift_url}"
    if ! curl -fSL "$swift_url" -o "/tmp/${swift_tarball}"; then
        die "failed to download the fallback Swift toolchain from ${swift_url}. Install Swift manually and re-run."
    fi
    tar -xzf "/tmp/${swift_tarball}" -C "$install_root" --strip-components=1

    local swift_bin="${install_root}/usr/bin"
    if [ ! -x "${swift_bin}/swift" ]; then
        die "fallback toolchain extracted but '${swift_bin}/swift' is missing/not executable."
    fi

    # Persist PATH for future shells (idempotent: only append once).
    local profile="${HOME}/.bashrc"
    local path_line="export PATH=\"${swift_bin}:\$PATH\""
    if ! grep -qF "$path_line" "$profile" 2>/dev/null; then
        printf '\n# Added by spikes/ios-xtool/scripts/setup-wsl.sh (R-02 fallback)\n%s\n' "$path_line" >> "$profile"
        log "appended Swift PATH to ${profile}; open a new shell or 'source ${profile}'."
    fi
    export PATH="${swift_bin}:$PATH"

    log "swift installed via fallback: $(swift --version 2>&1 | head -n1)"
}

install_swift

# ---- 2b. Compatibility shims for the 24.04 toolchain on Ubuntu 26.04 ------
#
# The 24.04-tagged Swift toolchain links against older library sonames that
# Ubuntu 26.04 renames (R-02 fallout). We add versioned symlinks pointing the
# old soname at the new one. The libxml2 2.x -> 2.15 (so.16) ABI used by
# swift-sdk/libSwiftPM is compatible in practice for these entry points.
#
# Each shim is created only if the old soname is missing AND the new one exists,
# so this is idempotent and never clobbers a real library.
install_compat_shims() {
    local libdir="/usr/lib/x86_64-linux-gnu"
    # old soname -> new soname (same directory)
    local -a shims=(
        "libxml2.so.2:libxml2.so.16"
    )
    local pair old new
    for pair in "${shims[@]}"; do
        old="${pair%%:*}"
        new="${pair##*:}"
        if [ -e "${libdir}/${old}" ]; then
            continue  # real/old lib already present; leave it alone
        fi
        if [ ! -e "${libdir}/${new}" ]; then
            warn "compat shim skipped: ${new} not found in ${libdir}; swift-sdk may fail to load ${old}."
            continue
        fi
        log "creating compatibility symlink ${old} -> ${new}"
        sudo ln -sf "${new}" "${libdir}/${old}"
    done
}

install_compat_shims

# ---- 3. usbmuxd / libimobiledevice (Linux side of the device link) --------

install_device_tools() {
    log "installing usbmuxd / libimobiledevice (device link, Linux side)..."
    # NOTE (Ubuntu 26.04): libimobiledevice6 was renamed to libimobiledevice-1.0-6
    # and its glue library split into libimobiledevice-glue-1.0-0.
    # `zip` is required by xtool to package the signed .ipa before install.
    sudo apt-get install -y usbmuxd libimobiledevice-1.0-6 libimobiledevice-glue-1.0-0 libimobiledevice-utils zip

    # usbmuxd must be running for the device to be reachable.
    if command -v systemctl >/dev/null 2>&1 && systemctl list-unit-files 2>/dev/null | grep -q usbmuxd; then
        sudo systemctl enable --now usbmuxd || warn "could not enable usbmuxd via systemd (WSL may lack systemd)."
    else
        warn "systemd not managing usbmuxd (common on WSL). Start it manually if needed: 'sudo usbmuxd -f &'."
    fi
}

install_device_tools

# ---- 4. Windows-side notes (usbipd-win) -----------------------------------
#
# USB devices are NOT visible to WSL by default. usbipd-win runs on the WINDOWS
# HOST (PowerShell as Administrator), not inside WSL, and forwards the iPhone's
# USB interface into the WSL distro.

cat <<'EOF'

------------------------------------------------------------------------------
Windows host steps (run OUTSIDE WSL, in an elevated PowerShell on Windows):
------------------------------------------------------------------------------
  1. Install usbipd-win once:
         winget install --interactive --exact dorssel.usbipd-win
  2. Plug in the iPhone 13 Pro and list USB devices:
         usbipd list
  3. Bind the iPhone's BUSID once (Administrator):
         usbipd bind --busid <BUSID>
  4. Attach it into WSL (repeat after each replug / WSL restart):
         usbipd attach --wsl --busid <BUSID>
  5. Back INSIDE WSL, confirm the device is seen:
         idevice_id -l        # should print the iPhone UDID
         ideviceinfo          # should print device info

If 'idevice_id -l' prints nothing, re-check the usbipd attach step and that
usbmuxd is running inside WSL.
------------------------------------------------------------------------------

xtool itself: install per the upstream xtool docs (it is the signer/installer
front-end). This script does not fetch xtool; smoke.sh checks for it and errors
clearly if absent. Signing uses YOUR Apple ID, entered interactively by xtool
at sign time — no credential is stored by these scripts.
------------------------------------------------------------------------------

EOF

log "setup complete. Next: connect the iPhone, attach via usbipd-win, then run scripts/smoke.sh."
