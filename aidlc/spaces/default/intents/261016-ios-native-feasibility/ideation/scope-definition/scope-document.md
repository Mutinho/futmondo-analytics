# Scope Document — App nativa iOS (Swift) desde Angular + xtool

> Fase: ideación. Define la frontera in/out, el MVP, la secuenciación por fases y el value
> stream. Fuentes: intent-statement, feasibility-assessment, constraint-register, respuestas
> `[QS<n>]`/`[QF<n>]`/`[Q<n>]`, reglas `[memory:M<n>]`.

## Frontera de alcance (in / out)

### Dentro (in-scope del plan de implementación v1)

| Capacidad | Nota | Source |
|-----------|------|--------|
| Spike de la cadena `xtool` end-to-end | App Swift mínima: build en WSL → firma gratuita → instalación en iPhone 13 Pro; valida R-01. | [QS1] [QF2] |
| Login (auth nativa) | Access token en memoria + refresh token en **iOS Keychain**; consume `/auth/*`. | [QS2] [QF4] [memory:M2] |
| Mercado | Reescritura SwiftUI de `features/market`; consume la API de mercado. | [QS2] [QS3] [Q6] |
| Presupuesto | Reescritura SwiftUI de `features/budget`; consume `/api/v1/analytics/balances`. | [QS2] [QS3] [Q6] |
| Favoritos (fase posterior, dentro de las 5) | Nice-to-have; tras el MVP. | [QS3] [Q6] |
| Calculadora (fase posterior, dentro de las 5) | Nice-to-have; tras el MVP. | [QS3] [Q6] |
| Exploración documentada de widgets | Viabilidad con `xtool` + firma gratuita; idea de widget de presupuesto/mercado; **no se implementa en v1**. | [QS4] [QF2] |

### Fuera (out-of-scope)

| Excluido | Motivo | Source |
|----------|--------|--------|
| App Store pública / distribución a terceros | Uso personal, instalación privada. | [Q8] |
| Android / Samsung A17 | iOS-only. | [Q2] [Q8] |
| Cambios en backend FastAPI / Fly.io / Neon | Backend intacto; salvo D-01 como dependencia a vigilar, no a ejecutar. | [Q8] [QF4] |
| Notificaciones push | Requieren cuenta de pago/APNs; inviable a coste 0 €. | [QS4] (R-03) |
| Implementación de widgets en v1 | Diferida a fase futura (sólo se documenta su viabilidad). | [QS4] |
| Pantallas no núcleo (finances, stats, evolution, clausulable, classification, transactions, my-roster, analytics) | Fuera de la primera versión nativa. | [Q6] [Q8] |
| Apple Developer Program (~99 €/año) | No se activa por defecto; sólo salida opcional si la firma gratuita resulta inasumible. | [memory:M1] [QF3] |

## MVP (primer hito usable)

**MVP = Login + Presupuesto + Mercado.** [QS2] Login valida la cadena técnica (y R-01 vía el
spike previo); Presupuesto + Mercado aportan el primer valor de uso real. [QS1] [QS2]

## Secuenciación por fases (risk-first)

| Fase | Contenido | Objetivo | Source |
|------|-----------|----------|--------|
| F0 — Spike | App Swift mínima instalada en el iPhone con `xtool` desde WSL; validar ciclo de refirmado ~7 días. | Despejar R-01 antes de invertir en pantallas. | [QS1] [QF2] |
| F1 — Login | Cliente de red Swift + auth (Keychain) + pantalla de login. | Base técnica validada end-to-end. | [QS1] [QF4] |
| F2 — MVP datos | Presupuesto + Mercado en SwiftUI. | Primer valor usable (MVP). | [QS2] [QS3] |
| F3 — Núcleo completo | Favoritos + Calculadora. | Completar las 5 funciones núcleo. | [QS3] |
| F-fast-follow (opcional) | Widget de resumen (presupuesto/mercado). | Exploración de widgets ya documentada. | [QS4] |

## Value stream (de capacidad a resultado)

El resultado para el usuario (una app iOS nativa de Futmondo, instalable a coste 0 €) se
alcanza encadenando: cadena de build validada (F0) → sesión nativa segura (F1) → consulta de
presupuesto y mercado desde el móvil como app nativa (F2) → cobertura núcleo (F3). Cada fase
entrega algo verificable en el iPhone, no sólo código. [QS1] [QS2]

## Assumptions & Open Questions

- [assumption] El reparto must/nice y la secuenciación pueden ajustarse si el spike (F0)
  revela fricciones; la ruta es reversible. [QS1] [QF2]
- [assumption] La exploración de widgets asume que el soporte de App Extensions de `xtool`
  con cuenta gratuita se confirma en la práctica. [QS4] [QF2]
