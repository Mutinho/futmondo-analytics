# Test Results — Build and Test (`data_manager_v2` decomposition)

Ejecución real de la suite backend tras la descomposición, para confirmar
equivalencia estricta (nada roto) y el piso de cobertura. Entorno: venv efímero
a coste 0 (Python 3.14 local, excluyendo `libsql-experimental`; CI corre 3.12),
`JWT_SECRET` efímero no productivo, fakes in-memory (sin red/BD/credenciales).

## Estado del build

- **Build**: N/A de compilación (Python). Instalación de dependencias OK
  (versiones fijadas exactas de `requirements.txt`, sin `libsql-experimental`).
- **Runner readiness**: `pytest --collect-only` OK; `pytest 9.1.1`.

## Resultados de la suite

| Métrica | Valor |
|---|---|
| Comando | `cd backend && JWT_SECRET=… python -m pytest tests/ --cov=app -q` |
| Total | 414 passed, 3 xfailed |
| Fallos | 0 |
| Skipped | 0 (3 xfailed esperados: tests LEGACY de `futmondo_client`, marcados xfail por diseño en un intent previo) |
| Cobertura (line, total) | **57.48%** |
| Piso bloqueante | `--cov-fail-under=27` → "Required test coverage of 27% reached" |
| Duración | ~78 s |

Baseline pre-refactor (del `code-summary.md`): 346 passed / 3 xfailed, 45.94%.
Delta: **+68 tests de caracterización**, cobertura **+11.54 pp**. El trinquete
sólo subió; el piso nunca se relajó (BR6.1/NFR2).

## Detalle de fallos

Ninguno. Los 3 `xfailed` son los tests LEGACY esperados de
`test_futmondo_client_characterization.py` (ajenos a este intent; documentan la
deuda de señal de fallo de integración, ya marcada xfail).

## Equivalencia (characterization-first)

Cada uno de los 14 módulos extraídos tiene green-pre == green-post (mismas
aserciones antes y después de extraer), según `code-summary.md`. La suite
completa verde confirma que los consumidores y el SQL-en-router intactos
(BR4.1) siguen funcionando y que la superficie de 57 métodos es equivalente
(BR1.1/BR3.1).

## Target Verification Matrix

Ver `build-and-test-summary.md` → `## Target Verification Matrix` (finalizada,
sin `Pending`).

<!-- Sin ## Loop-Back Log: no se disparó ningún loop-back (la etapa pasó en el primer intento). -->
