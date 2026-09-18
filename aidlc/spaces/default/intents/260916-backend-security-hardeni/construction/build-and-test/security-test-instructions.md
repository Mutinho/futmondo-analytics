# Instrucciones de Test de Seguridad — Backend Security Hardening

> Generadas pese a la estrategia Minimal porque el intent ES un patch de
> seguridad: los tests dirigidos por FR de esta etapa SON los tests de
> seguridad. Perspectiva de ingeniería de seguridad (STRIDE, acotado al intent).

## Cobertura STRIDE ↔ FR (acotada)

| Amenaza STRIDE | FR | Test que la cubre |
|----------------|----|-------------------|
| Tampering / Elevation (input malicioso de puja) | FR6 | `tests/test_market_bid_validation.py` — `price<=0` → 422 sin efecto lateral |
| Spoofing / Auth (validez de refresh token) | FR9 | `tests/test_auth_characterization.py`, `tests/test_durable_session_characterization.py` |
| Information disclosure (exposición de endpoints) | FR7 | `tests/test_photos_exposure.py` — ruta protegida; estáticas públicas a propósito |
| Spoofing / MITM (TLS) | FR8 | `tests/test_tls_verification.py` — sin `verify=False`; sin `SSL_VERIFY=0` |
| Elevation of privilege (admin destructivo) | FR18 | `tests/test_db_admin_guard.py` — 404 por defecto |

## Cómo ejecutar (desde `backend/`)

```bash
python -m pytest tests/test_market_bid_validation.py \
                 tests/test_auth_characterization.py \
                 tests/test_durable_session_characterization.py \
                 tests/test_photos_exposure.py \
                 tests/test_tls_verification.py \
                 tests/test_db_admin_guard.py -q
```

## Escaneos de seguridad del gate de CI (bloqueantes)

- **gitleaks**: escaneo de secretos, BLOQUEANTE en `.github/workflows/ci.yml`
  (PR→`main`). Verifica que ninguna corrección introduce credenciales en claro.
- `pip-audit` / `npm audit`: advisory (no bloqueante) en la fase de saneamiento.

## Invariantes de seguridad verificadas (no regresión)

- No se reintroduce la password Futmondo en claro (NFR1.7).
- No se usa `JWT_SECRET` por defecto en producción (NFR1.2; `test_jwt_startup.py`).
- No se abre ninguna ruta protegida ni se añade exclusión al middleware (NFR1.1).
- Ningún cliente HTTP de producción desactiva TLS (NFR1.8).

## Cobertura esperada

Minimal dirigido por FR: al menos un test por FR cubriendo el camino de error
donde aplica. Sin piso porcentual bloqueante adicional; la suite existente
permanece en verde.

## Fuera de alcance de esta etapa (defensa en profundidad, no bloqueante)

- El job `verify` de `fly-deploy.yml` (push→`main`) corre `pytest -q` sin
  `--cov` ni gitleaks: no idéntico al gate de MR. Documentado en `team.md`;
  su endurecimiento es diseño de pipeline, fuera de este intent.
