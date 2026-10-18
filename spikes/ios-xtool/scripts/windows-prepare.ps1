<#
.SYNOPSIS
    Prepara el lado Windows para instalar la app del spike xtool en el iPhone.

.DESCRIPTION
    Idempotente. Cada vez que vayas a instalar/reinstalar la app en el iPhone:
      1. Comprueba que el servicio "Apple Mobile Device" (usbmuxd de Apple) corre.
      2. Asegura el portproxy TCP 27015 -> 127.0.0.1:27015 (donde escucha el
         usbmuxd de Apple), para que WSL pueda hablar con el dispositivo.
      3. Asegura la regla de firewall de entrada para el puerto 27015.

    NO usa usbipd: en Ubuntu 26.04 + iPhone la via usbipd da 'muxError' al abrir
    el canal lockdown, asi que la instalacion va por el usbmuxd de Apple relayado
    por TCP (ver docs/spikes/ios-xtool.md, paso 2 y 3c).

.NOTES
    Ejecutar en PowerShell COMO ADMINISTRADOR.
    Requiere Apple Devices (Microsoft Store) o iTunes instalado en Windows.
#>

[CmdletBinding()]
param(
    [int]$Port = 27015
)

$ErrorActionPreference = 'Stop'

function Write-Step($msg) { Write-Host "[windows-prepare] $msg" -ForegroundColor Cyan }
function Write-Warn($msg) { Write-Host "[windows-prepare][warn] $msg" -ForegroundColor Yellow }
function Write-Err ($msg) { Write-Host "[windows-prepare][error] $msg" -ForegroundColor Red }

# --- 0. Comprobar privilegios de administrador ---------------------------
$principal = New-Object Security.Principal.WindowsPrincipal(
    [Security.Principal.WindowsIdentity]::GetCurrent())
if (-not $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
    Write-Err "Este script necesita PowerShell como Administrador."
    exit 1
}

# --- 1. Servicio de Apple (usbmuxd de Apple) ------------------------------
# El servicio se llama "Apple Mobile Device Service" (iTunes) o lo gestiona
# Apple Devices. Comprobamos y, si existe y esta parado, lo arrancamos.
$svc = Get-Service -Name 'Apple Mobile Device Service' -ErrorAction SilentlyContinue
if ($null -eq $svc) {
    Write-Warn "No se encontro 'Apple Mobile Device Service'. Asegurate de tener"
    Write-Warn "Apple Devices (Microsoft Store) o iTunes instalado y de que Apple"
    Write-Warn "Devices detecte el iPhone al menos una vez."
} else {
    if ($svc.Status -ne 'Running') {
        Write-Step "Arrancando 'Apple Mobile Device Service'..."
        Start-Service $svc
    }
    Write-Step "Apple Mobile Device Service: $((Get-Service $svc.Name).Status)"
}

# --- 2. Portproxy TCP $Port -> 127.0.0.1:$Port ----------------------------
$existing = netsh interface portproxy show v4tov4 | Select-String "0.0.0.0\s+$Port\s+127.0.0.1\s+$Port"
if ($existing) {
    Write-Step "Portproxy 0.0.0.0:$Port -> 127.0.0.1:$Port ya existe."
} else {
    Write-Step "Creando portproxy 0.0.0.0:$Port -> 127.0.0.1:$Port ..."
    netsh interface portproxy add v4tov4 listenaddress=0.0.0.0 listenport=$Port connectaddress=127.0.0.1 connectport=$Port | Out-Null
}

# --- 3. Regla de firewall de entrada --------------------------------------
$ruleName = "WSL usbmuxd $Port"
if (Get-NetFirewallRule -DisplayName $ruleName -ErrorAction SilentlyContinue) {
    Write-Step "Regla de firewall '$ruleName' ya existe."
} else {
    Write-Step "Creando regla de firewall '$ruleName' (TCP $Port entrante)..."
    New-NetFirewallRule -DisplayName $ruleName -Direction Inbound -Action Allow `
        -Protocol TCP -LocalPort $Port | Out-Null
}

# --- 4. Resumen -----------------------------------------------------------
Write-Host ""
Write-Step "Listo. Estado del portproxy:"
netsh interface portproxy show v4tov4

Write-Host ""
Write-Step "Siguiente: en WSL, ejecuta scripts/install-app.sh (recalcula la IP"
Write-Step "del gateway y lanza 'xtool dev run'). Manten el iPhone desbloqueado"
Write-Step "y confia el ordenador si lo pide."
