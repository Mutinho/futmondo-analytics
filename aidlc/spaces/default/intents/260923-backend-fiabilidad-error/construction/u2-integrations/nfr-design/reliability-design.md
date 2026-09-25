# Reliability Design — u2-integrations (Integraciones)

Diseño de los patrones de resiliencia de U2, derivado de
`reliability-requirements.md` (NFR2.1–2.3, NFR-rel.1) y las decisiones Q1/Q2 de
esta etapa. Núcleo del intent: taxonomía recuperable/fatal, timeout acotado,
no-corrupción de datos. Adaptado a Fly.io (crons one-shot, sin estado entre
ejecuciones), coste 0 €.

Consume: `reliability-requirements.md`, `functional-spec.md`, `contract-summary.md`.
Perspectivas inline: arquitecto + plataforma.

## Patrones de resiliencia

### Timeout acotado por petición (Q1 → NFR-rel.1 / NFR-perf.1)
- **Diseño**: cada llamada de integración fija un timeout explícito
  **connect ~5 s, read ~30 s** — vía el parámetro `timeout` de `requests`
  (Futmondo) y el equivalente de `curl_cffi` (Sofascore).
- Un exceso de timeout se traduce en `IntegrationTimeoutError` (recuperable):
  el paso se marca `DEGRADED` y el sync continúa.
- **Sin retry/backoff** (fuera de alcance del intent): recuperable = detectar +
  degradar, no reintentar.

### Manejo de baneo de Sofascore (Q2 → fatal simple)

- **Diseño**: un 403 → `IntegrationBanError` (fatal). El paso sofascore aborta
  limpio (sin escribir datos a medias), se registra `ERROR` estructurado, y el
  sync **continúa con los pasos independientes** de Sofascore.
- Un paso posterior que dependa del dato de Sofascore no obtenido se degrada
  como **recuperable** (`DEGRADED`), no se inventan datos.
- **Sin circuit breaker persistente**: los crons Fly son one-shot (sin estado
  entre ejecuciones); un breaker persistente exigiría almacenar estado — sobre-
  ingeniería a coste 0 €. La medida anti-baneo es el **throttle preventivo
  existente (~750 ms)**, que se mantiene sin cambio.

### Taxonomía recuperable/fatal en el punto de captura

- `SyncService` captura con dos ramas `except` explícitas (fatal primero,
  recuperable después) antes del `except Exception` genérico (functional-design
  BR2.2). La elevación contextual (BR2.3): un recuperable en un punto de
  escritura con riesgo de corrupción se trata como fatal.

### No-corrupción de datos — reemplazo transaccional atómico (NFR2.1)

- **Diseño**: el reemplazo de `team_prizes` (`DELETE ... NOT IN (...)` +
  repoblado) se envuelve en una **transacción única**. Cualquier fallo dentro de
  la transacción → `rollback` completo → el conjunto previo queda íntegro (nunca
  estado mixto). Endurece el punto existente sin ampliar el god-file.
- Máquina de estados: `STABLE → IN_TXN → (COMMITTED | ROLLED_BACK) → STABLE`
  (functional-design §3).

## Objetivo de fiabilidad

### NFR4.1 — Sin regresión (garantía de proceso)

- **Diseño**: el endurecimiento es **aditivo** y vive tras una capa/función
  estrecha testeable (no se amplían los god-files ni el patrón SQL-en-router).
  Cada captura brownfield que se reclasifica y el contrato de `_make_request` se
  **caracterizan primero** (specs de comportamiento actual) antes de tocarlos, y
  se aseveran los specs de efecto por modo de fallo. La **suite `pytest`
  existente permanece en verde** en cada paso y el **gate CI bloqueante**
  (gitleaks + `pytest` + `ng test`) pasa antes de fusionar a `main`.

- **SLI informal** (heredado de nfr-requirements): ausencia de `DEGRADED`
  inesperado + no-corrupción verificada por spec. SLO formal con burn-rate →
  **NO-APLICA/diferido** (de pago).
- **Tolerancia a fallo puntual**: los crons reintentan en la siguiente ventana
  programada; recuperación por re-ejecución (sync idempotente-por-recomputación).

## Recuperación / rollback

- **Rollback de release**: mecanismo Fly.io (redeploy de la release anterior),
  runbook `docs/ROLLBACK.md` — **sin cambio**.
- **RTO/RPO numéricos**: no aplican como objetivos formales en U2 (proceso batch,
  recuperación por re-ejecución).

## NO-APLICA (adaptación a Fly.io + coste 0 €)

- Multi-AZ / auto-scaling / failover gestionado → NO-APLICA (topología fija
  `min=max=1`, coste 0 €). Documentado, no inventado.
- Circuit breaker gestionado / retry con backoff → fuera de alcance (Q2 de esta etapa: fatal simple, sin breaker persistente; y exclusión de retry/backoff a nivel de intent).

## Assumptions & Open Questions

None.
