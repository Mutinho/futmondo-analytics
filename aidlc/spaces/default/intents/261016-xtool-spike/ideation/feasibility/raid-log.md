# RAID Log — Spike de la cadena `xtool` (B-01)

> Risks, Assumptions, Issues, Dependencies del spike. Hereda R-01 del estudio de viabilidad
> previo (`261016-ios-native-feasibility`) y lo concreta para la validación en vivo.

## Risks

| ID | Riesgo | Prob. | Impacto | Mitigación | Source |
|----|--------|-------|---------|------------|--------|
| R-01 | El USB passthrough WSL→iPhone (`usbipd-win` + `usbmuxd`) no logra enlazar el iPhone 13 Pro para firmar/instalar. | Media | Alto (bloquea el DONE) | Atacar este eslabón primero; documentar cada paso; si falla, registrar como hallazgo bloqueante y evaluar alternativa. | [Q2] [desc] |
| R-02 | No hay toolchain Swift oficial para Ubuntu 26.04 (binarios publicados para 22.04/24.04). | Media | Medio | Usar `swiftly` o toolchain etiquetado 24.04 por compatibilidad glibc; documentar la vía que funcione. | [Q1] |
| R-03 | La firma con Apple ID gratuito no basta para instalar en dispositivo (límites de cuenta gratuita). | Baja-Media | Alto | Documentar como hallazgo; NO comprar Apple Developer Program en este spike (decisión posterior con datos). | [memory:M1] |
| R-04 | `xtool` exige una versión de Swift concreta incompatible con la instalable en 26.04. | Baja | Medio | Alinear versión de Swift con la que pida `xtool`; si choca, degradar a toolchain 24.04. | [Q1] |

## Assumptions

| ID | Supuesto | Source |
|----|----------|--------|
| A-01 | Se dispone de Apple ID gratuito y de condiciones para conectar el iPhone 13 Pro por USB al PC con WSL. | [Q5] |
| A-02 | WSL2 ya operativo (confirmado: Ubuntu 26.04, kernel microsoft-standard-WSL2). | [Q1] |
| A-03 | La caducidad ~7 días de la firma gratuita y el refirmado quedan fuera del foco (materia de B-09). | [desc] |

## Issues

| ID | Issue | Source |
|----|-------|--------|
| I-01 | None (sin issues abiertos al inicio del spike). | [Q5] |

## Dependencies

| ID | Dependencia | Estado | Source |
|----|-------------|--------|--------|
| D-02 | WSL + Swift 6.4 + usbmuxd | Parcial: WSL listo; Swift/usbmuxd se montan en el spike. | [desc] [Q1] |
| D-03 | Apple ID (gratuito) | Supuesta disponible (A-01). | [desc] [Q5] |

## Assumptions & Open Questions

None.
