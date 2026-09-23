# Instrucciones de tests de seguridad — Fiabilidad de la sync

> Conversation language: Spanish. Perspectiva devsecops (support inline).
> Estrategia Standard: no hay SAST/DAST nuevo en esta etapa (ESLint/ruff son
> advisory; gitleaks bloquea en CI). El único requisito de seguridad de la
> unidad (NFR5) se valida con un test funcional de frontera, ya presente.

## Alcance de seguridad de esta unidad

- **NFR5 — Endurecimiento de la validación de entrada del `price`** (defensa en
  profundidad, independiente del frontend): el backend rechaza en la frontera
  `POST /api/v1/market/bid` un `price` fuera de rango (≤ 0 o > `PRICE_SANITY_CAP`)
  con **HTTP 422** antes de proxyar a Futmondo. Barrera contra overflow/abuso de
  un entero descontrolado.

## Cómo verificar

```bash
cd backend
python -m pytest tests/test_market_bid_sanity_cap.py -ra
```

Aserciones de seguridad (reales, sin red):
- `price > PRICE_SANITY_CAP` → 422 y el cliente Futmondo **NO** es invocado
  (no se propaga una puja abusiva).
- `price <= 0` → 422 (validación existente, sin regresión).
- `price` válido intermedio → 200 e invoca al cliente mockeado.

## Guardarraíles de seguridad honrados (devsecops)

- **Secretos**: ningún literal en código ni en tests; los tests de auth/arranque
  usan `JWT_SECRET` efímero no productivo. `gitleaks` escanea también los tests
  y es **bloqueante** en CI (PR) y en `verify` (push→`main`).
- **`JWT_SECRET` no-default**: exigido en arranque (NFR1.1), sin cambios por esta
  unidad.
- **Manejo de errores**: el estrechamiento de `except` (FR3.2) mejora la postura
  de seguridad/observabilidad: los fallos reales de migración dejan de tragarse
  silenciosamente.

## Deuda diferida (fuera de alcance, registrada)

- **SAST/DAST del frontend** y análisis estático de seguridad más allá de ESLint
  advisory: preexistente, diferido a un futuro diseño de pipeline (Q8=A). No lo
  cierra este intent.

## Sources

- `inception/requirements-analysis/requirements.md` (NFR5, NFR1.1),
  `functional-design/functional-spec.md` (FS3), `team.md`/`project.md`
  (guardarraíles de secretos y gitleaks).

## Assumptions & Open Questions

None.
