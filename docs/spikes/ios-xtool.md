# Runbook — Spike de la cadena `xtool` (B-01)

Guía reproducible para atravesar la cadena completa de `xtool` desde WSL
(Ubuntu) hasta un dispositivo físico: **build → firma gratuita → instalación →
arranque** de una app Swift/SwiftUI mínima en el **iPhone 13 Pro**.

El objetivo de este spike es **validar el toolchain**, no entregar una app. El
criterio de DONE es que la app arranque en el dispositivo y muestre la pantalla
trivial `xtool OK` + versión.

> El código del spike vive en `spikes/ios-xtool/`. Este runbook referencia los
> dos scripts de ese directorio: `scripts/setup-wsl.sh` y `scripts/smoke.sh`.

## Prerequisitos

- **Windows host** con WSL2 y una distro Ubuntu.
- **`usbipd-win`** instalado en el **host Windows** (no dentro de WSL) para
  reenviar el USB del iPhone a WSL.
- **iPhone 13 Pro** con cable USB y un **Apple ID** (cuenta gratuita válida).
- **`xtool`** instalado en WSL (front-end de firma/instalación), según su
  documentación oficial.
- Conexión a internet para descargar el toolchain Swift la primera vez.

> **Coste 0 €**: todo el flujo usa una cuenta Apple gratuita. La firma gratuita
> caduca a los **~7 días**; basta re-ejecutar `smoke.sh` para refrescarla.

## 1. Setup del entorno WSL

Desde la raíz del repo, en WSL:

```bash
spikes/ios-xtool/scripts/setup-wsl.sh
```

El script es **idempotente** y:

- Detecta la versión de Ubuntu.
- Instala el **toolchain Swift**. En **Ubuntu 26.04** (entorno vivo) no hay
  binario oficial de Swift (los oficiales apuntan a 22.04/24.04), así que el
  script intenta primero `swiftly` y, si no resuelve, cae al **toolchain
  etiquetado para 24.04** como *fallback* documentado (riesgo **R-02**).
- Instala **`usbmuxd` / libimobiledevice** (lado Linux del enlace con el
  dispositivo).
- Imprime las **notas del lado Windows** para `usbipd-win`.

Si falta un prerequisito, el script **falla con un mensaje claro** (sin fallos
silenciosos).

## 2. Enlazar el iPhone a WSL — IMPORTANTE: usar el relay de Apple Devices, NO usbipd

> **Hallazgo clave (validado en vivo 2026-10-16):** en Ubuntu 26.04 + iPhone
> (iOS 27), `usbipd attach` reenvía el USB crudo y `idevice_id -l` ve el
> dispositivo, pero la conexión **lockdown falla con `muxError` / "Could not
> connect to lockdownd (-8)"**, así que la instalación NO funciona por esa vía.
> La solución oficial de `xtool` (issue #19) es **relayar el usbmuxd de Apple
> en Windows** por TCP y apuntar `xtool` a él con `USBMUXD_SOCKET_ADDRESS`.

Pasos del relay (los que funcionaron):

1. **Windows**: instalar **Apple Devices** (Microsoft Store) o iTunes. Conectar
   el iPhone, desbloquearlo y confiar; confirmar que **Apple Devices lo ve**
   (eso prueba que el usbmuxd de Apple gestiona el lockdown).
2. **Windows (PowerShell admin)**: exponer el usbmuxd de Apple (escucha en
   `127.0.0.1:27015`) a WSL con un portproxy + regla de firewall:
   ```powershell
   netsh interface portproxy add v4tov4 listenaddress=0.0.0.0 listenport=27015 connectaddress=127.0.0.1 connectport=27015
   New-NetFirewallRule -DisplayName "WSL usbmuxd 27015" -Direction Inbound -Action Allow -Protocol TCP -LocalPort 27015
   ```
   (No hace falta `usbipd attach` para el iPhone en esta vía.)
3. **WSL**: apuntar `xtool` al usbmuxd remoto. La IP es el gateway por defecto
   (cambia entre reinicios de WSL; obtener con `ip route show default`):
   ```bash
   export USBMUXD_SOCKET_ADDRESS="$(ip route show default | awk '{print $3; exit}'):27015"
   xtool devices   # debe listar el iPhone
   ```

> La vía `usbipd` (bind/attach) queda documentada como **NO válida para
> instalar** en este entorno; sirve solo para que `idevice_id` liste el UDID.

## 2b. Login y SDK de xtool (una sola vez)

```bash
export PATH="$HOME/.local/bin:$HOME/.swift/usr/bin:$PATH"   # xtool + swift
xtool setup   # login modo "Password" con Apple ID gratuito; pide el Xcode.xip
```

> **Hallazgos clave del SDK (validados en vivo):**
> - `xtool` necesita **Xcode 27** (`Xcode.xip`, descarga autenticada de Apple,
>   varios GB). Genera `iPhoneOS27.1.sdk` etc.
> - El SDK se construye con **Swift 6.4**, así que el toolchain DEBE ser
>   **6.4.0** (el que `xtool` pinnea en su `Dockerfile`). Con 6.0.3 falla "this
>   SDK is not supported by the compiler"; con 6.4.1 falla al construir los
>   módulos Clang de `Foundation`.
> - El Darwin SDK hay que **generarlo con el toolchain 6.4.0 ACTIVO en el
>   PATH**. Si se generó con otro toolchain, reinstalarlo:
>   `xtool sdk install /ruta/Xcode_27.1.xip` (reutiliza el `.xip`, no re-descarga).

## 3. Build + firma + instalación (con el relay)

Desde `spikes/ios-xtool/`, con Apple Devices viendo el iPhone y el portproxy
activo:

```bash
export PATH="$HOME/.local/bin:$HOME/.swift640/usr/bin:$PATH"   # Swift 6.4.0
export USBMUXD_SOCKET_ADDRESS="$(ip route show default | awk '{print $3; exit}'):27015"
cd spikes/ios-xtool
xtool dev run    # build -> sign -> package -> install -> launch
```

El build se cachea, así que las reinstalaciones (p. ej. tras la caducidad de
~7 días) son rápidas. `xtool` pide tu Apple ID de forma interactiva solo la
primera vez (el token dura ~1 año). Los scripts no almacenan credenciales.

## 3c. Flujo RECURRENTE (cada vez que quieras instalar/abrir la app)

El setup pesado (toolchain, SDK, login) es de una sola vez. Para una
reinstalación posterior hay **dos scripts** que automatizan todo:

**a) Windows (PowerShell como Administrador), una vez por arranque de Windows:**
```powershell
spikes\ios-xtool\scripts\windows-prepare.ps1
```
Asegura (idempotente) el servicio Apple Mobile Device, el portproxy TCP 27015 y
la regla de firewall. (El portproxy normalmente persiste; el script lo re-crea
si falta.)

**b) WSL, cada vez que quieras instalar:**
```bash
~/futmondo-analytics/spikes/ios-xtool/scripts/install-app.sh
```
Recalcula la IP del gateway de WSL, exporta `USBMUXD_SOCKET_ADDRESS`, verifica
que `xtool` ve el iPhone y lanza `xtool dev run` (build cacheado = rápido).

Checklist humano cada vez: iPhone **conectado y desbloqueado**, "Confiar"
aceptado, y Apple Devices viéndolo. Tras un refirmado (~7 días), **confiar el
certificado** en Ajustes y abrir la app.

### Detalle manual equivalente (si no usas los scripts)

1. **Windows — conectar y desbloquear el iPhone.** Ábrelo y, si pregunta,
   "Confiar". Confirma que **Apple Devices** lo ve. (Si Windows no lo detecta,
   prueba otro puerto/cable; el BUSID puede cambiar, es normal.)
2. **Windows — el portproxy del 27015.** Normalmente **persiste** entre
   reinicios de Windows (la regla `netsh portproxy` y la de firewall quedan
   guardadas). Si alguna vez falla, revísalo con
   `netsh interface portproxy show v4tov4` y, si no está, vuelve a añadirlo
   (paso 2 de arriba). **No** necesitas `usbipd` en esta vía.
3. **WSL — arrancar usbmuxd local si hiciera falta.** Sólo si reiniciaste WSL:
   `pgrep usbmuxd || sudo usbmuxd -f &` (en la práctica, con el relay a Windows
   no es imprescindible, pero no estorba).
4. **WSL — recalcular la IP del relay y lanzar.** El gateway de WSL **cambia**
   entre reinicios, así que recalcúlalo cada sesión:
   ```bash
   export PATH="$HOME/.local/bin:$HOME/.swift640/usr/bin:$PATH"
   export USBMUXD_SOCKET_ADDRESS="$(ip route show default | awk '{print $3; exit}'):27015"
   cd ~/futmondo-analytics/spikes/ios-xtool
   xtool devices        # debe listar el iPhone antes de instalar
   xtool dev run        # reinstala y relanza (build cacheado = rápido)
   ```
5. **iPhone — confiar el certificado la primera vez tras cada refirmado** y
   abrir la app.

> **Resumen de la gestión del USB en el flujo recurrente:** NO uses
> `usbipd bind/attach` para el iPhone — esta vía va por **Apple Devices
> (Windows) + portproxy 27015 + `USBMUXD_SOCKET_ADDRESS`**. Lo único que cambia
> casi siempre es la **IP del gateway de WSL** (recalcúlala en el paso 4) y, por
> la **caducidad de ~7 días** de la firma gratuita, repetir `xtool dev run`.

> **Atajo opcional:** puedes meter el `export USBMUXD_SOCKET_ADDRESS=...` en tu
> `~/.bashrc` recalculándolo con el gateway, para no escribirlo cada vez.

## 4. Smoke manual (aceptación del DONE)

1. En el iPhone 13 Pro, localizar el icono de la app **`XToolSpike`**.
2. Primer arranque de una app con firma gratuita: ir a
   **Ajustes > General > Gestión de dispositivos y VPN** y **confiar** en el
   certificado de desarrollador (tu Apple ID).
3. Abrir la app. **Éxito** = muestra la pantalla `xtool OK` + la versión.
4. Capturar una foto/registro de `xtool` y anotarlo en **## Hallazgos**.

## Notas de firma gratuita

- La firma de una cuenta Apple gratuita caduca a los **~7 días**: la app deja de
  abrir hasta refirmar. Re-ejecutar `smoke.sh` resuelve el ciclo.
- `xtool` prefija el `bundleID` por cuenta; el `com.example.xtoolspike` de
  `xtool.yml` es solo una base placeholder.

## Hallazgos

**VEREDICTO: GO (validado end-to-end el 2026-10-16).** La app `XToolSpike`
construida, firmada (Apple ID gratuito) e instalada con `xtool` desde WSL
**arranca en el iPhone 13 Pro físico** y muestra `xtool OK version 1.0.0`.
Riesgo R-01 cerrado.

Entorno real validado:
- WSL2 **Ubuntu 26.04 LTS**; iPhone 13 Pro (`iPhone14,2`), **iOS 27.0.1**.
- **Swift 6.4.0** (toolchain etiquetado ubuntu24.04, instalado en `~/.swift640`).
- **xtool 1.22.2** (AppImage en `~/.local/bin`).
- **Xcode 27.1** (`Xcode.xip`) → SDK `iPhoneOS27.1.sdk`.
- Firma: modo **Password** con Apple ID gratuito; Team ID obtenido; token ~1 año.

Fixes necesarios en Ubuntu 26.04 (ya aplicados en `setup-wsl.sh`):
- Añadir `libncurses6` (el toolchain 24.04 busca `libncurses.so.6`).
- Symlink de compatibilidad `libxml2.so.2 -> libxml2.so.16`.
- Paquetes renombrados: `libimobiledevice-1.0-6` + `libimobiledevice-glue-1.0-0`.
- Añadir `zip` (xtool lo usa para empaquetar el `.ipa`).

Correcciones en el proyecto del spike:
- `xtool.yml`: `version` es el **schema version (entero `1`)**, no la versión de
  la app.
- `Package.swift` debe exponer **un `library` product** (no `executable`).

Secuencia de versiones (crítica): toolchain **6.4.0** emparejado con SDK de
Xcode 27.1, y **el SDK regenerado con 6.4.0 activo**. 6.0.3 y 6.4.1 fallan.

## Bloqueos observados

- **`muxError` / lockdownd (-8) sobre usbipd**: con `usbipd attach`,
  `idevice_id -l` ve el iPhone pero `ideviceinfo`/instalación fallan al abrir el
  canal lockdown. **Resuelto** relayando el usbmuxd de **Apple Devices (Windows)**
  por TCP 27015 (`netsh portproxy` + `USBMUXD_SOCKET_ADDRESS`). Es el bloqueo
  más importante del flujo y su solución está en el paso 2.
- **Fricción recurrente**: la IP del gateway de WSL cambia entre reinicios (hay
  que recalcular `USBMUXD_SOCKET_ADDRESS`); la firma gratuita caduca a ~7 días
  (re-ejecutar `xtool dev run`); el iPhone debe estar desbloqueado y visible en
  Apple Devices.
- **Coste de entrada**: descarga de `Xcode.xip` (varios GB, autenticada) y de los
  toolchains Swift (~1 GB cada uno). Una sola vez.
