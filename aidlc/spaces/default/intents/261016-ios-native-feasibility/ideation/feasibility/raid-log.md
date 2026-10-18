# RAID Log — App nativa iOS (Swift) + xtool

> Risks, Assumptions, Issues, Dependencies del estudio de viabilidad. Fuentes: respuestas
> `[QF<n>]`/`[Q<n>]`, reglas `[memory:M<n>]`, documentación oficial de `xtool`.

## Risks

| ID | Riesgo | Prob. | Impacto | Mitigación |
|----|--------|-------|---------|-----------|
| R-01 | La cadena `xtool` end-to-end (build Swift → firma con cuenta gratuita → instalación en iPhone 13 Pro desde WSL) **no está validada en vivo**; podría fallar o requerir ajustes no triviales (USB passthrough, usbmuxd, firma). | Media | Alto (bloquea toda la ruta) | **Spike temprano obligatorio** antes de comprometerse: instalar una app Swift mínima en el iPhone con `xtool` siguiendo el tutorial "First app"; validar el ciclo de refirmado. [QF2] |
| R-02 | La **caducidad de ~7 días** de la firma gratuita resulta más molesta de lo previsto en uso real. | Media | Medio | Proponer flujo de reinstalación de bajo esfuerzo (`xtool dev` scriptado desde WSL); si inasumible, evaluar Apple Developer Program (C-O2). [QF3] [QF5] |
| R-03 | Capabilities que exijan cuenta de pago (push remoto, App Groups, iCloud, ciertos widgets) **no disponibles** con firma gratuita. | Media | Bajo (uso personal; el núcleo no las necesita) | Mantener la primera versión sin capabilities de pago; documentar límites. [QF3] |
| R-04 | **Esfuerzo de reescritura** del cliente (UI SwiftUI + red + modelos + estado) mayor de lo estimado, al no reutilizar código Angular. | Media | Medio | Alcance acotado a 5 pantallas núcleo; sin plazo; ruta por fases en scope-definition. [QF1] [Q6] [QF5] |
| R-05 | El **ajuste de `/auth/refresh`** para clientes nativos resulta necesario y toca el backend "intacto". | Baja-Media | Medio | Verificar el contrato de auth en un intent posterior; tratar como dependencia explícita (D-01), no sorpresa. [QF4] |
| R-06 | Deriva de versión del **Swift 6.4 toolchain** / `xtool` / WSL que rompa la cadena tras una actualización. | Baja | Medio | Fijar versiones conocidas que funcionen; documentar el entorno validado. [QF2] |

## Assumptions

| ID | Supuesto | A validar en |
|----|----------|--------------|
| A-01 | `xtool` soporta la ruta Swift nativo end-to-end en WSL en tu entorno. | Spike (R-01). [QF2] |
| A-02 | La firma gratuita caduca a ~7 días y se renueva reinstalando con `xtool`. | Spike (R-01/R-02). [QF3] |
| A-03 | `/auth/refresh` depende de cookie `HttpOnly` y puede requerir aceptar el token por header/body para clientes nativos. | Lectura del backend (intent posterior). [QF4] |
| A-04 | No hay requisitos regulatorios (uso personal). | Confirmado por decisor único. [Q7] |
| A-05 | Las 5 pantallas núcleo son especificables desde las features Angular homónimas (verificado que existen en el repo). | Reverse-engineering. [Q6] |

## Issues

| ID | Incidencia (ya conocida) | Estado |
|----|--------------------------|--------|
| I-01 | Reencuadre respecto a intent-capture: "partiendo del código Angular" ya no significa portar código, sino usarlo como especificación (Swift nativo reescribe). | Resuelto: aprobado explícitamente por el usuario; reflejado en el assessment. [QF1] |
| I-02 | Corrección de supuesto: "Calculadora" es `features/calculator` (feature propia), no Finanzas; "Favoritos" es `features/favorites`. | Resuelto: verificado contra el repo. [Q6] |

## Dependencies

| ID | Dependencia | Tipo | Nota |
|----|-------------|------|------|
| D-01 | Posible ajuste de `/auth/refresh` en el backend FastAPI para refresh basado en header/body (cliente nativo sin cookies). | Externa (backend, fuera de este intent) | Registrar; no ejecutar aquí. [QF4] [Q8] |
| D-02 | Entorno de build: WSL + Swift 6.4 toolchain + usbmuxd + USB passthrough. | Entorno | WSL ya operativo; faltan toolchain/usbmuxd si no están. [QF2] [QF3b] |
| D-03 | Apple ID gratuito con el iPhone registrado. | Externa (Apple) | Disponible. [QF3] |
| D-04 | Documentación oficial de `xtool` como referencia de la cadena. | Conocimiento | Consultada y verificada en esta etapa. [QF2] |

## Assumptions & Open Questions

- [assumption] Las probabilidades/impactos de los riesgos son estimaciones conservadoras de
  ideación, a refinar tras el spike. [QF2]
- [assumption] D-01 podría no ser necesaria si el backend ya acepta el refresh token por una
  vía alternativa; pendiente de verificar leyendo el código del backend. [QF4]
