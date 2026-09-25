# Cross-Unit Final Coverage — Build and Test (FR14 + FR15)

Intent: `260925-limpieza-config-residuos` (refactor, zero-Unit). Este es el gate
de cobertura a nivel de stage, no el límite de fase.

## Veredicto: PASS

Cada FR/NFR de `requirements.md` está cubierto con status `OK` (o `N/A`
justificado) en el `traceability.json` de code-generation, y su fichero objetivo
existe. No hay User Stories (etapa no ejecutada en este scope), así que no se
enumeran `AC`.

## Cobertura por elemento

| ID | Estado | Objetivo (fichero) |
|----|--------|--------------------|
| FR14.1.1 | OK | `backend/app/core/config.py` (cascada Turso/DATABASE_TYPE/POSTGRES retirada) |
| FR14.1.2 | OK | `backend/app/services/db_connection.py` (motor único Neon) |
| FR14.1.3 | OK | `backend/requirements.txt` (sin `libsql-experimental`) |
| FR14.1.4 | OK | borrados `backend/nixpacks.toml`, `entrypoint.sh`, `scripts/migrate_*_to_turso.py` |
| FR14.1.5 | OK | `backend/tests/test_db_engine_characterization.py` (caracterización path Neon) |
| FR14.1.6 | OK | `config.py`, `db_connection.py` (comentarios obsoletos retirados) |
| FR14.2.1 | OK | `config.py` + `backend/tests/test_config_hardcoded_ids.py` |
| FR14.2.2 | OK | `config.py` (`LEAGUE_ID` sin default legacy) + test |
| FR15.1.1 | OK | `backend/app/main.py` (canónico `/api/v1/matchdays`) + `test_matchdays_mount.py` |
| FR15.1.2 | OK | `main.py` (retirado `/v1/matchdays`) + test |
| FR15.2.1 | OK | `git rm` de 6 residuos trackeados |
| FR15.2.2 | OK | `.gitignore` (+`*:Zone.Identifier`, +`stitch_*/`) |
| FR15.2.3 | N/A | `node_modules.old-*/` y `*.db` ya no-trackeados — no-op documentado |
| NFR1 | OK | suite backend verde (208 passed, 3 xfailed), sin regresión |
| NFR2 | OK | sin bajar cobertura; `--cov` observability-only |
| NFR4 | OK | ediciones quirúrgicas; sin `ruff format` masivo; artefactos producidos |

## Elementos sin cubrir

Ninguno. Sin findings de cobertura.

## Deuda diferida registrada (no bloquea)

- `DATABASE_PATH` conservada en `config.py` (la usan `photo_service.py` y el
  god-file `data_manager_v2.py`); limpieza completa = deuda (R-02).
- Comentario obsoleto `_TursoCursorWrapper` en `data_manager_v2.py:519` (god-file,
  C2, no tocado; código duck-typed correcto).
- Asimetría de la señal `--cov` backend `ci.yml` vs `fly-deploy.yml verify`
  (deuda diferida afirmada; fuera de alcance).
