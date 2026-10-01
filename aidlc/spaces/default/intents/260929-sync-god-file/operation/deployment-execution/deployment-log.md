# Deployment Log — sync god-file refactor (dominio piloto `match_odds`)

Intent: `sync-god-file` · scope `refactor` · fase Operation (última etapa).

## Estado del despliegue

**Deploy de producción NO ejecutado en esta sesión** (por decisión aprobada, Q2=A).
El modelo es on-merge a `main`; el deploy real lo dispara `fly-deploy.yml` cuando el
humano fusiona el PR. Esta etapa documenta la **preparación** y el release path.

- **Rama**: `main` (working tree). Cambios del refactor **sin commitear**.
- **Cambios pendientes de release**:
  - Nuevo: `backend/app/services/sync/` (paquete + `match_odds/` con `domain/ports.py`,
    `infrastructure/match_odds_adapter.py`, `orchestrator.py`).
  - Modificado: `backend/app/services/data_sync_service.py` (`sync_match_odds` reducido
    a delegación fina; `sync_all()` intacto).
  - Nuevo test: `backend/tests/test_sync_match_odds_characterization.py`.
  - Artefactos del workflow AI-DLC bajo `aidlc/` y la codekb actualizada.

## Preparación pre-despliegue (checks)

| Check | Resultado |
|-------|-----------|
| Suite backend (`pytest --cov=app`) | 251 passed / 3 xfailed / 0 failed |
| Piso de cobertura `--cov-fail-under=27` | 34.56% ≥ 27 (cumplido, no relajado) |
| `ruff check` ficheros nuevos | All checks passed (sin format masivo) |
| Equivalencia funcional estricta | Verificada por `git diff` (orquestador byte-idéntico) + caracterización verde pre/post |
| Migraciones de BD | No requeridas (esquema Neon sin cambios) |
| Servicios dependientes | Neon PostgreSQL y APIs Futmondo/Sofascore sin cambios |
| Secretos | Sin secretos nuevos; `JWT_SECRET` productivo vía `fly secrets` sin cambios |

## Release path on-merge (a ejecutar por el humano)

1. `git add` de los ficheros nuevos/modificados (código + tests), commit con
   Conventional Commits en castellano (p. ej. `refactor(backend): extrae sync_match_odds a sync/match_odds/ (DDD)`).
2. Abrir PR a `main`. El gate de CI bloqueante (`ci.yml`: gitleaks + pip-audit +
   ruff + pytest con cobertura y piso + npm audit + ng test) debe pasar. Un rojo
   nunca llega a producción.
3. Squash-merge a `main`. El push a `main` dispara `fly-deploy.yml`:
   `verify` (replica del gate) → `deploy-backend` (`futmondo-api`) →
   `deploy-frontend` (`futmondo-app`) → `smoke-test` (`/health`).
4. Verificación de release: smoke test `/health` (5 reintentos, HTTP 200). Ver
   `smoke-test-results.md`.

## Rollback

Documentado en `../deployment-pipeline/rollback-runbook.md` y `docs/ROLLBACK.md`:
`fly releases rollback <vN>` (o redeploy de la imagen previa) ante smoke test rojo.
Trigger, pasos y limitación del estado en memoria ya documentados.

## Seguridad e implicaciones (fase Operation)

- **Sin cambios de controles de seguridad**: no se tocan IAM/red/cifrado; sin nueva
  superficie de ataque (mismo contrato REST, sin endpoints nuevos). `data_manager_v2.py`
  intacto. Sin credenciales en excepciones (BR4.2 preservado).
- **Revisión de seguridad**: no aplica cambio de infraestructura; gitleaks bloqueante
  en el gate cubre el escaneo de secretos del release.
