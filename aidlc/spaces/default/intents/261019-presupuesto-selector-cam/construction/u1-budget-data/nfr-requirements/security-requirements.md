# NFR Requirements — Security (U1 `u1-budget-data`)

> Fase: construcción. Unidad: `u1-budget-data`. Idioma: castellano; tokens técnicos verbatim en inglés.

## SR1 — Sin credenciales en claro ni en errores (NFR2)
- U1 reutiliza el `AuthService`/`NetworkClient` de F1: el access token vive en memoria, el refresh token en Keychain; U1 **no** introduce almacenamiento de credenciales nuevo.
- Las funciones de U1 (`BudgetService`, `ChampionshipService`) **nunca** incluyen password/token en el `message`, `localizedDescription` ni `debugDescription` de los errores propagados. Los `NetworkError` llevan modo de fallo + contexto no sensible (status HTTP y **path del endpoint**, p. ej. `/api/v1/analytics/balances`), **nunca la URL completa con query string** ni ningún valor de query (aunque hoy la query sólo lleve un `championship_id` no sensible, el contrato fija path-only para que el patrón siga seguro si una llamada futura pusiera un valor sensible en la query).

## SR2 — `UserDefaults` no almacena secretos
- `ActiveChampionshipStore` persiste **sólo** el `championship_id` activo (identificador no sensible) en `UserDefaults`. Nunca tokens ni datos de sesión.

## SR3 — Transporte
- Todas las llamadas van por HTTPS (el `URLSessionNetworkClient` de F1 rechaza base URL no-https en su init). U1 no abre canales nuevos.

## SR4 — Entradas
- Las respuestas del backend se decodifican con tipos `Codable` estrictos; campos ausentes del endpoint legacy se toleran como opcionales, sin ejecutar nada dinámico.

## Sources

- `aidlc/spaces/default/intents/261019-presupuesto-selector-cam/construction/u1-budget-data/functional-design/{functional-spec.md,rules.md}`
- `aidlc/spaces/default/intents/261019-presupuesto-selector-cam/inception/requirements-analysis/requirements.md` (NFR2)
- `aidlc/spaces/default/memory/project.md` (reglas durables de seguridad)

## Assumptions & Open Questions

None.
