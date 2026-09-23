# Diseño de dominio — Decisiones (ADRs)

> Conversation language: Spanish. Backend-only, coste 0 €, sin ampliar god-files.

## ADR-1 — Estado de paso `degraded` como valor de `progress[step].status`, no como estado de Tarea

- **Contexto**: FR3.1 requiere que un paso `prizes`/`phantoms` fallido deje de
  reportarse como éxito. El estado por-paso vive en `task.progress[step]` (dict
  JSON libre); el `status` de la Tarea es un ciclo de vida global distinto.
- **Decisión**: introducir `"degraded"` como valor del campo `status` **dentro**
  de `progress[step]`, no un nuevo estado de la Tarea.
- **Consecuencias**: cambio aditivo, sin migración de BD (`progress` ya es JSON
  libre en memoria y en el `TaskRecord` durable). El consumidor que lee
  `progress[step].status` distingue `done` de `degraded`. La Tarea global puede
  seguir `completed` aunque un paso quede `degraded` (semántica correcta: la sync
  terminó, pero un paso no-crítico se degradó).
- **Alternativas rechazadas**:
  - (a) Nuevo estado de Tarea `DEGRADED`: contamina el ciclo de vida global y
    obliga a decidir precedencia con `completed`; más invasivo.
  - (b) Mantener `done` + campo `error` (statu quo): el consumidor que mira
    `status` sigue viendo éxito — no resuelve FR3.1.

## ADR-2 — Helper estrecho `record_degraded_step` fuera del god-file

- **Contexto**: la regla afirmada prohíbe ampliar `data_sync_service.py`. El
  patrón de degradación se repite en `prizes` y `phantoms` y podría extenderse.
- **Decisión**: encapsular la escritura del estado degradado + log estructurado
  en un helper estrecho en un módulo propio, reutilizable.
- **Consecuencias**: el bucle de `sync.py` solo llama al helper; testeable en
  aislamiento; extensible a otros pasos sin tocar el god-file.
- **Alternativas rechazadas**: inline en cada `except` (duplica lógica, no testeable
  en aislamiento); método nuevo en el god-file (viola la regla afirmada).

## ADR-3 — Techo de `price` como constante documentada, sin red

- **Contexto**: FR6 pide un techo de sanidad; el rango dinámico del mercado está
  fuera de alcance (acopla al estado del campeonato / god-file, coste).
- **Decisión**: constante `PRICE_SANITY_CAP` (múltiplo holgado del presupuesto
  máximo plausible), validada en `place_bid` junto al `price <= 0` existente.
- **Consecuencias**: rechazo determinista con 422, testeable con un umbral fijo;
  sin llamada de red. El valor exacto se fija en functional-design.
- **Alternativas rechazadas**: rango dinámico (fuera de alcance); sin techo
  (statu quo, deja pasar valores absurdos al proxy).

## ADR-4 — `except` acotados: recuperable vs fatal, por locus en alcance

- **Contexto**: FR3.2 pide reducir el `except` amplio silencioso, sin purga masiva.
- **Decisión**: en arranque/migraciones + camino de sync tocado, clasificar cada
  `except` como recuperable (log + continuar) o fatal (propagar); la tabla por
  locus se detalla en functional-design.
- **Consecuencias**: menos fallos tragados en los puntos críticos; diff acotado.
- **Alternativas rechazadas**: purga global de los ~159 `except` (refactor grande,
  fuera de apetito); no tocar nada (no cumple FR3.2).

## Sources

- Deriva de `components.md` (esta etapa) y `requirements.md`.
- Código verificado: `task_manager.py`, `task_service.py`, `sync.py`, `market.py`.

## Assumptions & Open Questions

- Valor de `PRICE_SANITY_CAP` y tabla recuperable/fatal: functional-design.
