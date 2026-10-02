# Deployment Log — `261001-sync-god-file-resto`

> Despliegue a producción **disparado por el humano** (on-merge/push a `main`).
> El conductor documenta el procedimiento; NO ejecuta el push ni el deploy.
> Estado: **pendiente de disparo humano**. Idioma: castellano.

## Artefacto a desplegar

- Refactor del dominio `clauses`: nuevo paquete
  `backend/app/services/sync/clauses/` + `data_sync_service.py` adelgazado +
  `tests/test_sync_clauses_characterization.py`. Equivalencia funcional estricta.
- Sin dependencias nuevas, sin cambios de esquema, sin cambios de API/superficie.

## Pre-deployment checks

| Check | Estado |
|-------|--------|
| Suite backend verde | OK (259 passed, 3 xfailed preexistentes) |
| Piso de cobertura `--cov-fail-under=27` | OK (35.73%) |
| `ruff check` ficheros nuevos | OK |
| Superficie pública preservada (10 claves `sync_all`, worker intacto) | OK |
| Migraciones de BD | No requeridas |
| Servicios dependientes (Neon, Futmondo) | Sin cambios de integración |

## Procedimiento de despliegue (a ejecutar por el humano)

1. Revisar y commitear los cambios (el conductor NO lo hace automáticamente):
   ```bash
   git add backend/app/services/sync/clauses backend/app/services/data_sync_service.py \
           backend/tests/test_sync_clauses_characterization.py
   git commit -m "refactor(backend): extrae el dominio clauses de sync al patron DDD (equivalencia estricta)"
   ```
   (más los artefactos AI-DLC bajo `aidlc/` si se desean versionar en el mismo commit).
2. Empujar a `main` (dispara `fly-deploy.yml`):
   ```bash
   git push origin main
   ```
3. El pipeline ejecuta: `verify` (gate bloqueante) → `deploy-backend` →
   `deploy-frontend` → `smoke-test` `/health`.
4. Verificar el resultado del smoke test en el workflow (ver `smoke-test-results.md`).

## Ventana de despliegue

Sin ventana formal (single-maintainer). El gate bloqueante y el smoke test son la
salvaguarda.

## Estado

**PENDIENTE** — a la espera de la acción de push a `main` del humano. El conductor
no ejecuta despliegues a producción.
