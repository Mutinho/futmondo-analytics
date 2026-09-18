# Resultados de Build and Test — Backend Security Hardening

> Scope `security-patch`, estrategia Minimal, brownfield, zero-Unit.
> Ejecutado en venv efímero (Python 3.14 del sistema, excluyendo
> `libsql-experimental`, `JWT_SECRET` efímero no productivo). Coste 0 €.

## Estado del Build

**Éxito.** El «build» de este patch es la verificación de la suite del backend
(no hay compilación nueva). Instalación de dependencias correcta (excluyendo
`libsql-experimental`, que no compila en 3.14 y no lo ejercitan los tests).

## Resultados de Tests

Suite completa (`python -m pytest -q` desde `backend/`): **135 passed, 1 warning**.

- Baseline previo al intent: 125 passed.
- Neto: +10 casos (nuevos/actualizados por las cinco correcciones).
- Sin fallos, sin regresiones, sin tests saltados.
- La warning (`StarletteDeprecationWarning` de `TestClient`) es preexistente y
  ajena a este patch.

### Resultados por FR (comandos scoped, deduplicados)

| FR | Comando | Resultado |
|----|---------|-----------|
| FR6 | `pytest tests/test_market_bid_validation.py` | 3 passed |
| FR7 | `pytest tests/test_photos_exposure.py` | 3 passed |
| FR8 | `pytest tests/test_tls_verification.py` | 2 passed |
| FR9 | `pytest tests/test_auth_characterization.py` | 12 passed |
| FR9 | `pytest tests/test_durable_session_characterization.py` | 3 passed |
| FR18 | `pytest tests/test_db_admin_guard.py` | 5 passed |

Sin doble conteo: el fichero de instrucciones stage-level lista comandos scoped
por FR; cada comando distinto se ejecutó una vez, y la suite completa una vez.

### Detalle de fallos

Ninguno.

### Cobertura

Sin piso porcentual bloqueante en el repo (`pytest-cov` disponible; no hay
`cov-fail-under`, decisión de equipo — ratcheting diferido). Cobertura dirigida
por FR: cada corrección tiene al menos un test verificable cubriendo el camino
de error donde aplica.

## Matriz de Verificación de Targets

| Target ID | Fuente | Esperado | Actual | Evidencia | Etapa propietaria | Veredicto |
|-----------|--------|----------|--------|-----------|-------------------|-----------|
| NFR1.3 (FR9) | security-requirements.md | Refresh token aware futuro → válido; expirado/revocado → inválido | Correcto | `test_auth_characterization.py` (12 passed), `test_durable_session_characterization.py` (3 passed) | build-and-test | Met |
| NFR1.4/1.5 (FR6) | security-requirements.md | `price<=0` → 422 sin efecto lateral | Correcto | `test_market_bid_validation.py` (3 passed) | build-and-test | Met |
| NFR1.6 (FR7) | security-requirements.md | `/api/v1/photos` protegido; estáticas públicas documentadas | Correcto | `test_photos_exposure.py` (3 passed) | build-and-test | Met |
| NFR1.8 (FR8) | security-requirements.md | Sin `verify=False`; sin `SSL_VERIFY=0` | Correcto | `test_tls_verification.py` (2 passed) | build-and-test | Met |
| NFR1.9 (FR18) | security-requirements.md | Endpoints admin → 404 salvo `ENABLE_DB_ADMIN` | Correcto | `test_db_admin_guard.py` (5 passed) | build-and-test | Met |
| NFR4 (no regresión) | project.md / team.md | Suite existente en verde | 135 passed | `pytest -q` | build-and-test | Met |
| NFR-PERF | performance-test-instructions.md | (sin target de rendimiento en el intent) | N/A | Inventario sin target de perf | N/A | N/A |
| gitleaks (cambios del patch) | ci.yml | Los cambios del patch no introducen secretos | Sin secretos nuevos | gitleaks (Docker) ejecutado localmente; el único hallazgo es preexistente y ajeno a los ficheros de este patch (ver abajo) | build-and-test | Met |

## Hallazgo de seguridad — secreto preexistente en el historial de git

Con el sombrero de ingeniería de seguridad puesto, ejecuté **gitleaks** vía
imagen Docker oficial (coste 0) sobre el repositorio como comprobación adicional
del gate. Resultado: **1 leak**, y es importante clasificarlo con precisión:

- **Fichero**: `backend/app/api/v1/endpoints/auth.py`, línea 34 (regla
  `generic-api-key`).
- **Commit**: `5a226084`, fecha **2025-11-11** (autor `iampatxo`), ~10 meses
  ANTES de que empezara este intent (2026-09-16).
- **Estado**: el fichero **ya no existe** en el árbol de trabajo actual; el
  hallazgo vive únicamente en el HISTORIAL de git.
- **Relación con este patch**: **ninguna.** Ninguno de los ficheros que tocan
  las cinco correcciones (`token_store.py`, `market.py`, `main.py`,
  `docker-compose.yml`, los tests) es ese fichero, y ninguno introduce un
  literal de secreto.
- **¿Bloqueará el gate de CI de este PR?**: **no.** El gate usa
  `gitleaks/gitleaks-action@v3` en evento `pull_request`, que escanea **solo los
  commits del PR**, no todo el historial. El leak preexistente no está en los
  commits de este patch. Mi ejecución local con `detect` escaneó los 183 commits
  del historial completo, por eso apareció.

**Recomendación (fuera del alcance de este intent, elevada como hallazgo):**
rotar/revocar la credencial afectada y considerar purgar el historial (o
añadir una excepción `.gitleaksignore` justificada si ya está revocada). Es un
trabajo de seguridad independiente, no una regresión de este patch.

## Evaluación de Readiness

- **Build-ready**: sí (suite verde).
- **Test-ready**: sí (todos los tests dirigidos por FR + suite completa en verde).
- **Deployment-ready**: sí, condicionado al gate de CI bloqueante (gitleaks +
  pytest + ng test) que se ejecuta en el MR antes de fusionar a `main` (NFR4).

## Limitaciones conocidas

- gitleaks y `ng test` (frontend) no se ejecutan en esta verificación local;
  son gate bloqueante de CI. Este patch no toca el frontend.
- Reproducción local requiere excluir `libsql-experimental` en Python > 3.12.
