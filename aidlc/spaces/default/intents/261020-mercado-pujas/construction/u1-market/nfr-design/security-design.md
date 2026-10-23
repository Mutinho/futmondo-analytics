# Security Design — u1-market

> Diseño de seguridad de `u1-market` (kind `ui`). Mapea los `NFR3.x` a patrones
> concretos. No introduce criptografía ni almacenamiento nuevos: reutiliza la
> cadena de auth de F1 y refuerza las garantías para la novedad de F3 (escritura
> + 2º endpoint externo).

## Sources

- `.../construction/u1-market/nfr-requirements/security-requirements.md` (NFR3.1–NFR3.8).
- `.../construction/u1-market/functional-design/functional-spec.md` (W4–W7).
- `aidlc/spaces/default/memory/{project,team}.md` (reglas durables de credenciales).
- `nfr-design-questions.md` (Q2).

## Arquitectura de autenticación / autorización

```
MarketView/SofascoreDetailSheet
      │ (acción)
      ▼
MarketViewModel ──► MarketService / SofascoreService (actor)
                          │ APIRequest
                          ▼
                 NetworkClient (F1, reutilizado)
                   • inyecta Authorization: Bearer <access token> (provider síncrono TokenHolder)
                   • rechaza base URL no-https en init (SEC-N1)
                          │ HTTPS
                          ▼
                 Backend FastAPI (autoridad de validación)
```

| NFR | Patrón de diseño | Detalle |
|---|---|---|
| NFR3.1 | Bearer por request | Toda `APIRequest` de Mercado/Sofascore pasa por `NetworkClient`, que añade `Authorization: Bearer` leyendo el `TokenHolder` (snapshot síncrono del token en memoria). |
| NFR3.2 | Access token en memoria | El token lo posee el actor `AuthService` (F1) y se expone al `NetworkClient` vía `TokenHolder` (NSLock), sin persistirse. |
| NFR3.3 | Refresh token en Keychain | Reutiliza `KeychainTokenStore` (F1); `u1-market` no añade almacenamiento de secretos. |
| NFR3.4 | Validación en dos capas | **Cliente** (`BidAmountValidator`, UX): `[market_price, available_for_bids]` y `>0`. **Backend** (autoridad): `price>0`, `price≤5e9`; su rechazo → `.rejected`. La UI nunca es la única barrera. |
| NFR3.5 | TLS obligatorio | Base URL `https`; `URLSessionNetworkClient.init` lanza ante no-https (defensa en el límite de red). |
| NFR3.6 | Avisos sin credenciales | El mapeo `MarketWriteOutcome` construye el aviso con el `message`/`detail` del backend o un texto genérico; nunca incluye token/password ni `exc_info` con material de credencial. |
| NFR3.7 | Sin secretos en código/tests | Ningún token/secreto hardcodeado; los XCTest usan dobles in-memory; gitleaks escanea el árbol. |
| NFR3.8 | Escritura autenticada sin bypass | `placeBid`/`cancelBid` usan la misma sesión Bearer; no hay ruta de escritura sin auth; refresh/401 lo gestiona la capa `AuthService` existente. |

## Defensa en profundidad (resumen)

1. **Transporte**: TLS obligatorio, rechazo de no-https (NFR3.5).
2. **Identidad**: Bearer en memoria + refresh en Keychain `ThisDeviceOnly`
   (NFR3.2/NFR3.3).
3. **Validación**: cliente (UX) + backend (autoridad) (NFR3.4).
4. **No divulgación**: avisos y logs sin material de credencial (NFR3.6/NFR3.7).

## Manejo de 401 / refresh

Reutiliza el patrón de F1: ante `401`, `AuthService` intenta un refresh
coalescido (una sola tarea in-flight) con el refresh token de Keychain vía el
header `X-Refresh-Token`; si falla, se fuerza logout. `u1-market` no reimplementa
esto; sus servicios propagan el `NetworkError.unauthorized` a la capa de sesión.

## Assumptions & Open Questions

None.
