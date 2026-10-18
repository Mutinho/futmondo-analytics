# Constraint Register — App nativa iOS (Swift) + xtool

> Restricciones técnicas, organizativas y regulatorias que acotan el estudio y la futura
> implementación. Fuentes: respuestas `[QF<n>]`/`[Q<n>]`, reglas de memoria `[memory:M<n>]`,
> documentación oficial de `xtool`.

## Restricciones técnicas

| ID | Restricción | Origen | Impacto |
|----|-------------|--------|---------|
| C-T1 | Build/firma/deploy iOS **sin Mac**, sólo Windows **vía WSL** con `xtool`. | [QF4] [QF3b] [desc] | Toda la cadena depende de `xtool` + WSL + Swift 6.4 + usbmuxd + USB passthrough. |
| C-T2 | Ruta de framework fijada a **Swift/SwiftUI nativo puro**. | [QF1] | El cliente se reescribe entero; el Angular existente es sólo especificación. |
| C-T3 | Backend FastAPI + Fly.io + Neon **intacto** en este alcance. | [Q8] [QF4] | Cualquier necesidad de cambio (p. ej. `/auth/refresh`) es dependencia externa, no trabajo de este intent. |
| C-T4 | Refresh token en **iOS Keychain**, nunca en claro. | [QF4] [memory:M2] | Diseño de sesión del cliente nativo condicionado por regla de seguridad durable. |
| C-T5 | `xtool` con cuenta gratuita **prefija el bundle ID** (`XTL-xxxx.`). | [QF3] (doc xtool) | Bundle ID no controlable del todo; impacto bajo en uso personal. |
| C-T6 | Dispositivo objetivo: **iPhone 13 Pro** (iOS), uso personal. | [Q2] | SwiftUI con target iOS acorde al dispositivo; sin matriz de dispositivos amplia. |

## Restricciones económicas / organizativas

| ID | Restricción | Origen | Impacto |
|----|-------------|--------|---------|
| C-O1 | **Coste recurrente 0 €** (tiers gratuitos). | [memory:M1] [desc] | Firma gratuita como ruta por defecto; sin servicios de pago recurrentes. |
| C-O2 | **Excepción acotada**: Apple Developer Program (~99 €/año) admisible SOLO como coste de distribución nativa, a comparar y como salida opcional. | [memory:M1] [QF3] | No se activa por defecto; se documenta como alternativa. |
| C-O3 | **Sin plazo**; proyecto personal, decisor único. | [QF5] [Q7] | Optimizar por esfuerzo razonable y aprendizaje, no por fecha. |

## Restricciones de alcance (producto)

| ID | Restricción | Origen | Impacto |
|----|-------------|--------|---------|
| C-S1 | **iOS-only**; Android fuera. | [Q2] [Q8] | No se analiza Android pese a existir un Samsung A17. |
| C-S2 | Sin **App Store pública** para terceros; instalación personal/privada. | [Q8] | Firma gratuita/ad-hoc suficiente; sin review de App Store. |
| C-S3 | Primera versión = **5 funciones núcleo** (Login, Mercado, Presupuesto, Favoritos, Calculadora). | [Q6] | El resto de pantallas, diferido. |
| C-S4 | UI nativa **dentro** del análisis como portabilidad, no rediseño visual desde cero. | [Q8] | Se analiza el esfuerzo de rehacer UI en SwiftUI, no un rediseño de marca. |

## Restricciones regulatorias / compliance

| ID | Restricción | Origen | Impacto |
|----|-------------|--------|---------|
| C-R1 | No se identifican requisitos regulatorios (PCI/HIPAA/SOC2/residencia de datos) para un uso personal de datos de fantasy football. | [Q7] [assumption] | Sin obligaciones de compliance formal en este alcance. |
| C-R2 | Cumplir los **términos de Apple** para firma gratuita / instalación en dispositivo propio. | (doc xtool) [QF3] | Instalación limitada a dispositivos propios; sin distribución a terceros. |

## Assumptions & Open Questions

- [assumption] Ausencia de requisitos regulatorios: asumida por tratarse de uso personal; no
  hay stakeholder legal que lo contradiga. [Q7]
- [assumption] Los límites de cuenta gratuita de Apple (C-T5 y afines) se confirmarán en el
  spike de `xtool`. [QF3]
