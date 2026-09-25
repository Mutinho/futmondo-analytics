# Integration Test Instructions — Construction (FR3.2 + FR4)

Estrategia **Standard** → tests de integración en las fronteras clave. Backend
`pytest` desde `backend/`, con las fixtures de `conftest.py`, sin red, sin DB
real, sin credenciales (gitleaks escanea). Coste 0 €.

## Fronteras clave cubiertas (U1↔U2 y borde de sync)

Los tests de la unidad U2 ya ejercitan las fronteras de integración clave (no se
crea un árbol de tests paralelo nuevo; van bajo `backend/tests/`):

| Frontera | Test | Qué verifica |
|---|---|---|
| U1↔U2: jerarquía `IntegrationError` | `tests/test_futmondo_client_typed_failures.py` | `_make_request` lanza el subtipo correcto (timeout/request/unparseable) y sin credenciales en `str`/`repr` |
| Contrato `_make_request` (pre-migración) | `tests/test_futmondo_client_characterization.py` | congela el contrato actual + inventario de llamadores núcleo/deuda (3 legacy marcados `xfail` tras la migración) |
| Punto de captura del sync → estado | `tests/test_sync_integration_failure_effect.py` | recuperable → paso `DEGRADED` vía `SyncStepStatus` y la operación NO falla; fatal (baneo) → excepción propagada y sin datos a medias |
| Escritura `team_prizes` (no-corrupción) | `tests/test_team_prizes_atomic_replacement.py` | fallo dentro de la transacción de reemplazo → conjunto previo íntegro (todo-o-nada) |
| Capa de errores U1 | `tests/test_integration_errors.py`, `tests/test_error_layer_hardening.py` | jerarquía y endurecimiento de U1 (regresión) |

## Cómo ejecutar (integración + suite completa)

```bash
cd backend && JWT_SECRET="<efímero>" python -m pytest tests -q
```

(La suite completa incluye los tests por-unidad y de integración; no hay entorno
externo que levantar — todo con dobles en memoria.)

## Cobertura esperada

- Cobertura significativa de las ramas de fallo nuevas y del reemplazo atómico.
- `--cov` es **observabilidad-only, sin piso bloqueante** en este intent
  (ratcheting diferido); NUNCA se baja un umbral para pasar el gate.

## Datos y entorno

- Todo en memoria (`_FakeInMemoryDB`/`_FakeCursor`), sin estado compartido mutable;
  `JWT_SECRET` efímero, nunca credenciales reales.
