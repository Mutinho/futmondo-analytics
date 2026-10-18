# Anomaly Detection Config — F1: Login nativo end-to-end

> Fase: operación (observability-setup). Idioma: castellano; tokens técnicos verbatim en inglés.
> **Anomaly detection por ML (CloudWatch Anomaly Detection) NO-APLICA**: es de pago y el stack es
> coste 0 €. Se sustituye por **barreras deterministas** (validación de entrada) y **estados
> explícitos**, coherente con `aidlc-shared/operation-fly-stack.md`.

## Decisión

- **No hay detección de anomalías por ML** en F1. Rationale: coste 0 € (ML gestionado de pago) y
  volumen bajo (single-maintainer) que no justifica baselining estadístico.

## Sustituto gratuito: deterministas + estados explícitos

- **Barreras deterministas**: validación de entrada en los endpoints de auth; el transporte del
  refresh token sigue una precedencia explícita (cookie → header `X-Refresh-Token` → body), no una
  heurística.
- **Estados explícitos**: el backend expresa fallo como estado/HTTP explícito (p. ej. 401 en
  credencial inválida, estados `degraded` donde aplique), no como señal implícita que requiera
  detección estadística.
- **Señal de "anomalía" efectiva**: el smoke `/health` en rojo y los picos de 4xx/5xx en
  `fly logs` (ver `alarms.md`/`log-queries.md`) son la detección práctica de comportamiento
  anómalo, sin ML.

## NO-APLICA (de pago)

| CloudWatch Anomaly Detection / stage | Estado |
|---|---|
| Baselining estadístico / ML | NO-APLICA; sustituido por barreras deterministas + estados explícitos |

## Sources

- [consumes] reliability-design.md, monitoring-design.md — NO existen (`skipped`); derivado de la
  app desplegada.
- [memory] aidlc-shared/operation-fly-stack.md (Anomaly Detection ML → deterministas + estados);
  project.md (coste 0 €).

## Assumptions & Open Questions

None.
