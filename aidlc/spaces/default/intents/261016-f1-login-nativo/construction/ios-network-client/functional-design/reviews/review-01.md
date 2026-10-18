## Review

**Verdict:** NOT-READY
**Reviewer:** aidlc-architecture-reviewer-agent
**Date:** 2026-10-17T17:05:26Z
**Iteration:** 1

### Findings

| ID | Severity | Location | Finding | Required action | Status |
|---|---|---|---|---|---|
| R-01 | Critical | functional-spec.md vs entities.md/contract-summary.md | Forma de `NetworkError` contradictoria entre fuentes (`transport(String)` vs `transport(Error)`). | Unificar a una forma autoritativa. | New |
| R-02 | Critical | NetworkError Equatable | `Error` no es `Equatable`; `NetworkError: Equatable` con payload `Error` no compila. | Payloads `String`/`Int`; convertir el Error crudo a String en el borde. | New |
| R-03 | Major | NR3 / send | 2xx vacío (204/body vacío) caería en `.decoding` pese a ser éxito. | Añadir `EmptyResponse` y tratar 2xx vacío como éxito. | New |
| R-04 | Major | NR3 | Mapeo incompleto: 4xx distintos de 401/403 (400/404/422) y 3xx indefinidos. | Añadir `.clientError(Int)` y `.unexpectedStatus(Int)`. | New |
| R-05 | Minor | APIRequest.body | `(any Encodable)?` no es codificable directo con JSONEncoder. | Usar `AnyEncodable` wrapper. | New |
| R-06 | Minor | NR3 | CancellationError agrupado en `.transport` podría disparar reintentos indebidos (ADR-4). | Añadir `.cancelled`. | New |

### Summary

Pase adversarial del functional-spec del cliente de red Swift. Dos Critical (forma de `NetworkError` contradictoria entre spec/entities/contrato; e incompatibilidad `Equatable` con payload `Error`) y dos Major (2xx vacío mal mapeado; mapeo de 4xx/3xx incompleto) impiden una implementación fiel. Aspectos sólidos: separación cliente-sesión-Keychain (delegada a Bolt 3), solo SDK de Apple, inyección de Bearer sin estado, posture de test honesta con P-1. NOT-READY: requiere revisión.
