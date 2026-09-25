# Feedback Loop — Feedback & Optimization (FR3.2 + FR4)

Bucle de feedback continuo a coste 0 €: qué observar en producción, la deuda
registrada que alimenta futuros intents, y las oportunidades de mejora.

## Qué vigilar (señales de producción)

- `fly logs --app futmondo-api | grep 'failure_mode='` — aparición y frecuencia
  de fallos de integración por modo.
- `level=ERROR failure_mode=ban` — baneos de Sofascore recurrentes → revisar
  throttle.
- Pasos `DEGRADED` **inesperados o repetidos** → señal de un proveedor externo
  inestable o de un `endpoint` problemático.
- Jobs de cron/deploy en rojo (notificación de GitHub Actions).

## Deuda registrada (entrada para futuros intents)

| Deuda | Motivo del diferimiento | Destino |
|---|---|---|
| Llamadores de `_make_request` en `roster.py` no migrados | núcleo vs deuda (FR4.3): sólo se migró donde un `None` corrompe datos | intent futuro de fiabilidad de endpoints de mercado |
| `except: pass` de `data_manager_v2.py` / `photo_service.py` | god-files fuera de alcance | **Intent 3** (descomposición de god-files) |
| Asimetría de la señal `--cov` (`verify` sin `--cov` vs `ci.yml` con `--cov=app`) | deuda de pipeline | intent de tooling CI |
| Piso de cobertura backend bloqueante (`cov-fail-under`) | ratcheting diferido | cuando la cobertura suba lo suficiente (el trinquete sólo sube) |
| `timeout=15` escalar de `_make_request` vs connect~5s/read~30s del diseño | pre-existente, fuera del diff | endurecimiento opcional futuro |
| 5 avisos `ruff check I` (orden de imports) en `futmondo_client.py` | regla de no reformatear brownfield en masa | se corrigen si el fichero se toca a fondo en otro intent |

## Oportunidades de optimización

- Extender la migración de contrato tipado al resto de llamadores (retirar la
  deuda de `roster.py`) en un intent acotado.
- Subir el trinquete de cobertura backend cuando haya masa crítica de tests.
- Considerar un timeout más fino por cliente si aparecen bloqueos largos en
  `fly logs`.

## Cierre del intent

Objetivo cumplido: los fallos de integración ya **no se enmascaran ni corrompen
datos**; son observables (log estructurado) y tratados por taxonomía
recuperable/fatal, con no-corrupción verificada. Coste 0 € mantenido. La deuda
queda registrada para continuidad.

## Assumptions & Open Questions

None.
