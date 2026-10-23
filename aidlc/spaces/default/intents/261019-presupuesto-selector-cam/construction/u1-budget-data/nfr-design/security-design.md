# NFR Design — Security (U1 `u1-budget-data`)

> Fase: construcción. Unidad: `u1-budget-data`. Idioma: castellano; tokens técnicos verbatim en inglés.

## Diseño de seguridad (cómo se cumplen SR1-SR4)

- **SR1 (no fuga en errores)**: `BudgetService`/`ChampionshipService` capturan los errores del `NetworkClient` y los propagan como `NetworkError` ya tipado por F1, cuyo contexto es `status` + `path` del endpoint. No se construye ningún string de error con la URL completa ni con la query; no hay `print`/`log` de credenciales. Un test comprueba que la descripción del error de una llamada fallida **no contiene** el `championship_id` ni ningún token. La aserción de no-fuga cubre **ambas rutas de error**: el `NetworkError` de red/status y el `DecodingError` de un response malformado (SR4) — el `DecodingError` de Foundation describe la ruta del tipo/clave, no el payload de credenciales, y aun así el test lo asevera explícitamente.
- **SR2 (UserDefaults)**: `UserDefaultsActiveChampionshipStore` escribe/lee sólo bajo la clave `futmondo_active_championship` un `String` (el id). No serializa objetos de sesión.
- **SR3 (HTTPS)**: hereda el `URLSessionNetworkClient` de F1, cuyo init lanza si la base URL no es https. U1 no crea clientes nuevos.
- **SR4 (decode estricto)**: `JSONDecoder` con los `Codable` definidos; los opcionales de `Championship` absorben el subconjunto legacy sin ejecutar nada dinámico.

## No hay superficie nueva

U1 no añade endpoints, almacenamiento de credenciales, ni dependencias. El modelo de amenazas no cambia respecto a F1.

## Sources

- `aidlc/spaces/default/intents/261019-presupuesto-selector-cam/construction/u1-budget-data/nfr-requirements/security-requirements.md`
- `aidlc/spaces/default/intents/261019-presupuesto-selector-cam/construction/u1-budget-data/functional-design/functional-spec.md`

## Assumptions & Open Questions

None.
