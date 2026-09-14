# Resultados de Build and Test

## Estado de ejecución (replay tras loop-back 1)

- Entorno: venv temporal local (coste 0€, efímero), dependencias del backend
  sin `libsql-experimental` (no requerida por estos tests; su wheel no compila
  en Python 3.14 local — el CI usa 3.12). `JWT_SECRET` = valor efímero del CI.
- Comando: `python -m pytest tests -q` (suite completa del backend).
- Resultado: **54 passed, 0 failed, 2 warnings** — TODA la suite en verde.

## Resultados de tests

- Total: 54 · Passed: 54 · Failed: 0 · Skipped: 0
- Los 3 tests objetivo (`test_championship_trends`, `test_clause_network`,
  `test_player_value_trend`) PASAN, junto con el resto de la caracterización.
- Warnings no bloqueantes: StarletteDeprecationWarning (httpx/testclient) e
  InsecureKeyLengthWarning (JWT de 12 bytes en un test de firma) — preexistentes,
  ajenos a este arreglo.

## Historial (primera ejecución, antes del loop-back)

Primera ejecución: 53 passed, 1 failed (`test_championship_trends`:
`'team-1' == 'Team One'`). Causa: `_safe_team_info` consultaba la BD directamente
y bajo el fixture no había BD, dejando `_team_cache` vacío. El `AttributeError`
previo enmascaraba este fallo. Resuelto en loop-back 1.

## Loop-Back Log

### Loop-back 1 — 2026-09-14T09:55:00Z
- **Diagnosis**: `test_championship_trends` falla en aserción (`'team-1' == 'Team One'`) tras resolver el AttributeError; `_safe_team_info` no usa el stub `get_team_by_id` porque consulta la BD directamente y bajo el fixture no hay BD.
- **Root-cause stage**: code-generation (alcance del arreglo del test).
- **Planned fix**: en `test_analytics_service.py`, poblar `_team_cache` en `fake_init` con los equipos del stub y marcar `_player_cache["__teams_loaded__"]=True` (Alternativa A), sin tocar producción.
- **Estimated impact**: effort bajo (un fichero de test); financial cost 0€; risk bajo.
- **Resultado**: aplicado y verificado — 54 passed, 0 failed.
