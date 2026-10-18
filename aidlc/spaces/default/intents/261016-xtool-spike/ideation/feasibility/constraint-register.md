# Constraint Register — Spike de la cadena `xtool` (B-01)

## Restricciones técnicas

| ID | Restricción | Tipo | Source |
|----|-------------|------|--------|
| C-T1 | El entorno de build es WSL2 (Ubuntu 26.04 LTS), no macOS/Xcode nativo; toda la cadena pasa por `xtool`. | Técnica | [desc] [Q1] |
| C-T2 | Toolchain Swift y `usbip` no instalados hoy; se montan dentro del spike. | Técnica | [Q1] |
| C-T3 | El USB passthrough al iPhone se hace vía `usbipd-win` + `usbmuxd`/libimobiledevice. | Técnica | [Q2] |
| C-T4 | La firma es de Apple ID gratuito (prefijo de bundle ID automático; caducidad ~7 días, fuera de foco). | Técnica | [desc] |
| C-T5 | Dispositivo objetivo fijo: iPhone 13 Pro físico. | Técnica | [desc] |

## Restricciones organizativas

| ID | Restricción | Tipo | Source |
|----|-------------|------|--------|
| C-O1 | Proyecto personal, un único mantenedor, sin plazo ni change-freeze. | Organizativa | [Q5] |

## Restricciones regulatorias / de coste

| ID | Restricción | Tipo | Source |
|----|-------------|------|--------|
| C-C1 | Coste 0 € estricto: firma gratuita, sin compra del Apple Developer Program en este spike; si no basta, se documenta como hallazgo. | Coste (dura) | [memory:M1] |

## Assumptions & Open Questions

None.
