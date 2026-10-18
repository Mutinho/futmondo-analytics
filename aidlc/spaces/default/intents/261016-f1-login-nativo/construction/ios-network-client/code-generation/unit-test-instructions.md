# Unit Test Instructions — `ios-network-client` (Bolt 2 de F1)

> Fase: construcción (code-generation). Idioma: castellano; identificadores/código en inglés.

## Verificación en este entorno

Los XCTest del `NetworkClient` son **lógica pura** y se ejecutan con **`swift test`** (SwiftPM)
sin iPhone y sin macOS, usando un `URLProtocol` stub. El **entorno del agente no tiene toolchain
Swift**, así que no se ejecutan aquí; el **propietario los corre con `swift test` en WSL** (Swift
6.4 del spike F0). Es verificación **real y reproducible** (opción A), no un placeholder.

## Cómo verificar (lo ejecuta el propietario, en WSL)

```bash
# tests unitarios del cliente de red (sin iPhone), verificacion real del bolt:
cd ios && swift test
# validacion end-to-end en el dispositivo (flujo visual; sobre todo en el Bolt 3):
cd ios && xtool dev build   # luego instalar en el iPhone 13 Pro
```

Verification Command del checkpoint: `cd ios && swift test` (comando real). El engine de este
entorno no puede ejecutarlo (sin Swift); el resultado lo aporta el propietario y se registra como
verificación.

## Tests escritos (XCTest, deuda P-1 para ejecución)

`NetworkClientTests.swift` con `URLProtocol` stub cubre: éxito 2xx con decodificación; 2xx vacío →
`EmptyResponse`; 401→`.unauthorized`; 403→`.forbidden`; otro 4xx→`.clientError`; 5xx→`.server`;
transporte→`.transport`; decoding inválido→`.decoding`; cancelación→`.cancelled`; inyección de
`Bearer` presente/ausente; init lanzable rechaza `http://`.

## Testing Contract

Methodology: test-after. Scope `feature` (piso 80% line-coverage aplica a código ejecutable con
runner; para Swift el runner/arnés es deuda P-1, verificación manual en F1). Solo SDK de Apple.

## Sources

- [consumes] functional-spec.md, requirements.md (NFR-3), team-practices (P-1).

## Assumptions & Open Questions

None.
