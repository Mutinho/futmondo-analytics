# Code Summary — U1 `u1-error-layer`

Capa de errores de integración: módulo nuevo de tipos, re-parentado del baneo de
Sofascore, y reclasificación characterization-first de las capturas amplias de la
primera oleada (arranque, migraciones, `db_connection`), más el commit de config
aislado de `E722`. Intervención acotada y aditiva; NO se amplían god-files. Coste
0 € (stdlib). Identificadores/docstrings/comentarios en inglés; mensajes de las
excepciones de integración en inglés.

## Archivos creados

| Archivo | Qué hace |
|---|---|
| `backend/app/services/integration_errors.py` | Jerarquía de tipos hoja: raíz `IntegrationError(failure_mode, *, status=None, endpoint=None)` + subtipos `IntegrationBanError` (fatal), `IntegrationTimeoutError` (recuperable), `IntegrationUnparseableError` (recuperable). Mensaje compuesto SOLO de campos no sensibles → ninguna credencial puede llegar a `str/repr/args` por construcción (NFR3, BR1.4). Sin lógica de decisión (la clasificación la codifica el tipo). |
| `backend/tests/test_integration_errors.py` | 15 tests: construcción de cada subtipo, clasificación recuperable/fatal por tipo, captura por la raíz, re-parentado de `SofascoreIPBanError`, y el spec de defensa NFR3 (credenciales de prueba ausentes en `str/repr/args`). |
| `backend/tests/test_error_layer_hardening.py` | 5 tests: caracterización + reclasificación aseverando el EFECTO — `_test_connection` propaga con BD muerta (fatal), `get_connection` hace rollback()+raise sin commit parcial (fatal, NFR2), fallo de creación de pool degrada a conexiones directas y el arranque continúa (recuperable). Dobles en memoria; sin `pytest.raises` sin aserción de estado. |

## Archivos modificados (quirúrgico)

| Archivo | Cambio |
|---|---|
| `backend/app/services/sofascore_client.py` | `SofascoreIPBanError` ahora hereda de `IntegrationBanError` (FR4.4). Se preserva su construcción por mensaje posicional y el comportamiento 403/re-raise (FR2.1) exactos; `failure_mode` fijado a `"ban"`. |
| `backend/app/main.py` | Clasificación RECUPERABLE explícita de las capturas de arranque (auth-tables, durable-session, durable-task schema+sweep): degradar a warning y continuar. Solo comentarios; sin cambio funcional. |
| `backend/app/services/db_connection.py` | Clasificación explícita: creación de pool RECUPERABLE (fallback a conexiones directas), `_test_connection` FATAL (propaga), y `get_connection` documentado como FATAL rollback()+raise, semántica transaccional **sin cambios** (NFR2, BR1.5). |
| `backend/scripts/migrate_to_turso.py` | Clasificación RECUPERABLE explícita del `except` de creación por tabla (una tabla que falla no aborta la migración idempotente). Solo comentario. |
| `backend/ruff.toml` | Quitado SOLO `E722` del `ignore` (se mantienen `E501`, `E402`): bare-except re-habilitado ADVISORY por trinquete; ruff sigue advisory. Cambio de config aislado, sin `--fix` ni `ruff format`. |

## Decisiones clave

- **Clasificación en el tipo, no en un helper**: siguiendo domain-design
  (Alternatives Rejected), `integration_errors` es un módulo de tipos puro; la
  decisión recuperable/fatal la codifica el subtipo y la acción la toma el punto
  de captura de la ruta de sync (U2). No se añade helper de clasificación.
- **No-filtración por construcción**: el constructor no acepta el request ni
  credenciales; la filtración es imposible, no vigilada.
- **`SofascoreIPBanError`**: se conserva la firma por mensaje de sus llamadores
  (`sofascore_client`, `sofascore_sync`, tests) para no romper FR2.1; se fija
  `failure_mode="ban"` y se mantiene el mensaje como texto de la excepción.
- **Endurecimiento quirúrgico**: las capturas de arranque/migraciones ya eran
  recuperables correctas (idempotentes, degradan y continúan) y las transacciones
  ya hacían rollback()+raise fatal; la reclasificación las hace explícitas y las
  congela con specs que aseveran el efecto, sin reestructurar ni ampliar
  god-files.

## Resultado de tests

- **Comando de unidad** `cd backend && python -m pytest tests/test_integration_errors.py tests/test_error_layer_hardening.py -q`: **20 passed**.
- **Suite completa**: **186 passed** (línea base 166 + 20 nuevos), sin regresiones.
- **`ruff check`** sobre los ficheros nuevos: limpio. `E722` ahora reporta 6
  avisos preexistentes en god-files/`photo_service` (deuda registrada, advisory,
  fuera de alcance de U1 — no se tocan).

## Trazabilidad

Ver `traceability.json` (FR4.1, FR4.4, FR3.2.1-3, NFR3 → BR1.1-1.6). El commit de
`E722` va aislado (`chore(ci)`); el resto del código nuevo/modificado en su commit.

## Assumptions & Open Questions

None.
