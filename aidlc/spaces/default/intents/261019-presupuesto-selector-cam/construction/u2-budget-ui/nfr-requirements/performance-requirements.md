# NFR Requirements — Performance (U2 `u2-budget-ui`)

> Fase: construcción. Unidad: `u2-budget-ui`. Idioma: castellano; tokens técnicos verbatim en inglés.

## PR1 — Render fluido (NFR4.1)
- La lista de equipos usa `List`/`LazyVStack` (render perezoso) para scroll fluido (objetivo 60 fps) con decenas de filas. Las filas son ligeras (texto + tokens, sin trabajo pesado en el cuerpo de la vista).

## PR2 — Feedback de carga inmediato (NFR4.1)
- Al iniciar `load()` o `selectChampionship`, el estado pasa a `loading` **síncronamente** antes del `await` de red → el indicador aparece <100 ms.

## PR3 — Verificación
- 60 fps y <100 ms son **observación en dispositivo** (iPhone 13 Pro); no medibles en WSL. El `swift build` sólo garantiza compilación.

## Sources

- `aidlc/spaces/default/intents/261019-presupuesto-selector-cam/inception/requirements-analysis/requirements.md` (NFR4)
- `aidlc/spaces/default/intents/261019-presupuesto-selector-cam/inception/refined-mockups/accessibility-checklist.md`

## Assumptions & Open Questions

None.
