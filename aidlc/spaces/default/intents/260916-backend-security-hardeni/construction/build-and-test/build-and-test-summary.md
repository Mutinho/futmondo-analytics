# Resumen de Build and Test — Backend Security Hardening

> Scope `security-patch`, estrategia Minimal, brownfield, zero-Unit. Cinco
> correcciones de seguridad (FR6, FR7, FR8, FR9, FR18).

## Estado global y prerrequisitos

- **Build**: éxito (verificación de suite; sin compilación nueva).
- **Prerrequisitos**: Python 3.12 en CI; venv efímero excluyendo
  `libsql-experimental` en local si Python > 3.12; `JWT_SECRET` no-default.
- Detalle completo de ejecución en `test-results.md`.

## Inventario de tipos de test generados

| Tipo | Generado | Motivo |
|------|----------|--------|
| Unit / dirigido por FR | Sí (en Code Generation) | Estrategia Minimal: 1+ test verificable por FR |
| Integración | No (nota en `integration-test-instructions.md`) | Minimal; el boundary HTTP ya se ejercita con TestClient en los tests por FR |
| Rendimiento | No (nota en `performance-test-instructions.md`) | Sin NFR de rendimiento en el intent |
| Seguridad | Sí (`security-test-instructions.md`) | El intent ES un patch de seguridad; mapeo STRIDE↔FR + gitleaks |

## Expectativas de cobertura

Dirigida por FR (Minimal). Sin piso porcentual bloqueante adicional (decisión de
equipo). Suite completa en verde como no-regresión (NFR4).

## Target Verification Matrix

| Target ID | Fuente | Esperado | Actual | Evidencia | Etapa propietaria | Veredicto |
|-----------|--------|----------|--------|-----------|-------------------|-----------|
| NFR1.3 (FR9) | security-requirements.md | Refresh token aware futuro → válido; expirado/revocado → inválido | Correcto | `test_auth_characterization.py` (12), `test_durable_session_characterization.py` (3) | build-and-test | Met |
| NFR1.4/1.5 (FR6) | security-requirements.md | `price<=0` → 422 sin efecto lateral | Correcto | `test_market_bid_validation.py` (3) | build-and-test | Met |
| NFR1.6 (FR7) | security-requirements.md | `/api/v1/photos` protegido; estáticas públicas documentadas | Correcto | `test_photos_exposure.py` (3) | build-and-test | Met |
| NFR1.8 (FR8) | security-requirements.md | Sin `verify=False`; sin `SSL_VERIFY=0` | Correcto | `test_tls_verification.py` (2) | build-and-test | Met |
| NFR1.9 (FR18) | security-requirements.md | Endpoints admin → 404 salvo `ENABLE_DB_ADMIN` | Correcto | `test_db_admin_guard.py` (5) | build-and-test | Met |
| NFR4 (no regresión) | project.md / team.md | Suite existente en verde | 135 passed | `pytest -q` | build-and-test | Met |
| gitleaks (cambios del patch) | ci.yml | Los cambios no introducen secretos | Sin secretos nuevos | gitleaks Docker; único hallazgo preexistente y ajeno (ver `test-results.md`) | build-and-test | Met |
| NFR-PERF | performance-test-instructions.md | (sin target de rendimiento) | N/A | Inventario sin target de perf | N/A | N/A |

Sin veredictos `Pending` ni `Unverified`: todos los targets aplicables `Met`;
una fila `N/A` para rendimiento.

## Evaluación de readiness

- **Build-ready**: sí.
- **Test-ready**: sí (135 passed; todos los FR verdes).
- **Deployment-ready**: sí, condicionado al gate de CI bloqueante del MR
  (gitleaks + pytest + ng test) antes de fusionar a `main`.

## Limitaciones / puntos abiertos

- **Hallazgo de seguridad elevado (fuera de alcance)**: gitleaks detecta un
  secreto **preexistente** en el historial de git (`auth.py`, commit 2025-11-11,
  fichero ya eliminado), ajeno a este patch y que el gate de CI del PR no
  marcará. Recomendación: rotar la credencial y purgar/ignorar el historial como
  trabajo de seguridad independiente. Detalle en `test-results.md`.
- `ng test` (frontend) y gitleaks del PR corren en CI; este patch no toca el
  frontend.
