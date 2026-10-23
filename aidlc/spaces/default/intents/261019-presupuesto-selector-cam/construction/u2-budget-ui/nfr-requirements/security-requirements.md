# NFR Requirements — Security (U2 `u2-budget-ui`)

> Fase: construcción. Unidad: `u2-budget-ui`. Idioma: castellano; tokens técnicos verbatim en inglés.

## SR1 — Sin credenciales en la UI (NFR2)
- La capa SwiftUI **no** maneja tokens ni credenciales: consume los servicios de U1 (que ya inyectan el `Bearer` vía el `NetworkClient` de F1). No hay almacenamiento de credenciales en vistas ni en el `BudgetViewModel`.
- Los mensajes de error que muestra `ErrorState` provienen del `BudgetState.error(String)`, que el VM construye a partir del **`localizedDescription`/modo de fallo del error tipado de U1 verbatim**, **sin interpolar** `championship_id`, el objeto de petición ni tokens. El VM nunca compone el string de error concatenando datos de la petición; sólo reexpone el mensaje no sensible que U1 ya garantiza (cadena de no-fuga heredada, cubierta por los tests de U1 para `NetworkError` y `DecodingError`).

## SR2 — Sin datos sensibles en `UserDefaults`
- El selector sólo persiste el `championship_id` activo vía el `ActiveChampionshipStore` de U1 (identificador no sensible).

## SR3 — Sin superficie de red nueva
- U2 no abre canales ni endpoints; toda la red pasa por U1 → `NetworkClient` de F1 (HTTPS forzado).

## Sources

- `aidlc/spaces/default/intents/261019-presupuesto-selector-cam/construction/u1-budget-data/nfr-design/security-design.md`
- `aidlc/spaces/default/intents/261019-presupuesto-selector-cam/inception/requirements-analysis/requirements.md` (NFR2)

## Assumptions & Open Questions

None.
