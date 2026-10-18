# NFR Validation Matrix — F1: Login nativo end-to-end

> Fase: operación (performance-validation). Idioma: castellano; tokens técnicos verbatim en inglés.
> Matriz target vs. actual de los NFR de F1 (`requirements.md`). F1 no tiene NFR de rendimiento
> cuantificado; la columna de rendimiento se valida por ausencia de regresión (ver `test-results.md`).

## Matriz NFR (target vs actual)

| NFR | Target | Actual / Evidencia | Estado |
|-----|--------|--------------------|--------|
| NFR-1 Seguridad de credenciales | Ningún token/credencial en claro (logs/excepciones/disco); refresh token solo en Keychain; `JWT_SECRET` no-default fail-fast | Refresh token en iOS Keychain (revisión de código `KeychainTokenStore` + flujo en dispositivo); guardarraíl de no-logging del body de D-01; `jwt_startup` sin cambios | ✅ Cumple |
| NFR-2 Coste 0 € | Sin dependencias de pago; solo SDK de Apple; firma gratuita | Cliente nativo solo SDK Apple; firma free-signing (~7 días); backend aditivo sin deps nuevas | ✅ Cumple |
| NFR-3 Compatibilidad de verificación | Backend build + `pytest` verdes + gate CI bloqueante; cliente nativo validado manualmente en iPhone 13 Pro | `pytest` 422 passed (incl. 8 de transporte); gate verde; `swift test` 29 passed; flujo validado en dispositivo | ✅ Cumple |
| NFR-4 Idioma | Identificadores/código/comentarios en inglés; UI/commits en castellano | Código Swift en inglés; UI/commits en castellano (convención afirmada) | ✅ Cumple |
| (Rendimiento) | Sin NFR de latencia/escala contractual en F1 | `/health` ~0.18 s en caliente; `/auth/login` ~0.42 s (dominado por Futmondo); D-01 sin latencia material añadida | ✅ Sin regresión |

## Observaciones

- F1 no declaró NFR de rendimiento/escalabilidad cuantificados; por eso la validación de
  rendimiento es de **no-regresión** con medición puntual gratuita, no de cumplimiento de SLO.
- Todos los NFR de F1 (seguridad, coste, verificación, idioma) están **cumplidos** con evidencia de
  etapas previas (build-and-test, deployment-execution) y de esta etapa.

## Sources

- [consumes] requirements.md (NFR-1..NFR-4); test-results.md, load-test-plan.md; dashboards.md.
- [consumes] performance-requirements.md, scalability-requirements.md — NO existen (`skipped`; F1
  sin NFR de rendimiento).
- [code] test-results.md (construction/build-and-test: 29 swift test + 422 pytest); mediciones en
  vivo.
- [memory] project.md (coste 0 €, no credenciales, idioma); aidlc-shared/operation-fly-stack.md.

## Assumptions & Open Questions

None.
