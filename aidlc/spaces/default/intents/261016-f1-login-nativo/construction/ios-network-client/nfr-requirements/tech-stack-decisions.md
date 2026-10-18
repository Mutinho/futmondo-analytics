# NFR — Tech Stack Decisions (`ios-network-client`)

> Bolt 2 de F1. Idioma: castellano; identificadores/código en inglés.

## TSD-N1 — Solo SDK de Apple
`URLSession`, `Codable`, `JSONEncoder/Decoder`, `async/await`. **Cero** dependencias SPM externas
(NFR-2/P-3). `AnyEncodable` es un wrapper propio trivial, no una dependencia.

## TSD-N2 — Swift Package Manager
El cliente vive como un target SwiftPM dentro del proyecto `xtool` (coherente con el flujo de build
del spike F0). Sin librerías de red de terceros (Alamofire descartado).

## TSD-N3 — Testabilidad diferida (P-1)
Diseño con `URLSession` inyectable para doblar con `URLProtocol` stub cuando exista el arnés XCTest
(deuda registrada). En F1, verificación manual en el iPhone.

## Sources
- [consumes] technology-stack.md, functional-spec.md, team-practices (P-1, P-3).

## Assumptions & Open Questions
None.
