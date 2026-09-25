# Cost Analysis — Feedback & Optimization (FR3.2 + FR4)

## Coste del intent: 0 € (confirmado)

| Recurso | Tier | Coste |
|---|---|---|
| Fly.io (backend + frontend, `min=max=1`, 256 MB) | free allowance | 0 € |
| Neon PostgreSQL (Frankfurt) | free tier | 0 € |
| GitHub Actions (CI + crons one-shot) | free | 0 € |
| Dependencias nuevas | **ninguna** (stdlib: `logging`, `requests`/`curl_cffi` ya presentes) | 0 € |

## Verificación del mandato

- **No se introdujo ninguna dependencia de pago** ni servicio con gasto
  recurrente (mandato afirmado ALWAYS coste 0 €).
- La reproducción local de tests usa un **venv efímero** (coste 0 €), excluyendo
  `libsql-experimental`.
- Todo lo que en el conocimiento AWS implicaría gasto (CloudWatch, X-Ray, SNS,
  KMS, load testing gestionado, anomaly ML) se marcó **NO-APLICA** con su
  alternativa gratuita.

## Optimización de coste

- No hay optimización de coste pendiente: el proyecto ya opera en tiers gratuitos
  con topología fija. No hay recursos ociosos que apagar (una máquina por app).

## Assumptions & Open Questions

None.
