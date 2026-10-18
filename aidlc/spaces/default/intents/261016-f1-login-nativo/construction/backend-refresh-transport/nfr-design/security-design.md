# NFR Design — Security Design (`backend-refresh-transport`)

> Bolt 1 de F1. Fase: construcción (nfr-design). Cómo se materializan los requisitos SEC-* en el
> diseño del handler. Idioma: castellano; tokens técnicos verbatim en inglés.

## Diseño de la resolución del refresh token (SEC-4)

Función pura y testeable, aislada del handler (firma canónica única; el handler la **invoca**, no
inlina el `or`):
```
def resolve_refresh_token(cookie: str | None, header: str | None, body_token: str | None) -> str | None:
    # Precedencia cookie -> header -> body, por VALOR NO VACÍO:
    # una cadena vacía cuenta como ausente (coherente con `or`).
    return cookie or header or body_token
```
- Determinista, por **presencia con valor no vacío** (`""` se trata como ausente). El handler
  llama a esta función y luego aplica la verificación/revocación existente. Testeable sin HTTP.
- Modelos de body (en `auth/models.py`):
  `class RefreshBodyOptional(BaseModel): refresh_token: Optional[str] = None` y
  `class LogoutBodyOptional(BaseModel): refresh_token: Optional[str] = None`. El `body_token` que
  recibe la función es `body.refresh_token if body else None`.

## SEC-1 (TLS) — diseño
Sin cambios de esquema de transporte: el endpoint se sirve tras HTTPS (Fly.io). `COOKIE_SECURE`
sigue gobernando la cookie. No se añade ningún binding en claro.

## SEC-2 (no-logging) — diseño
- El handler **no** registra `token`, ni `body`, ni headers de credencial.
- Si se añade un log de diagnóstico, registra solo el **canal** (`"cookie"|"header"|"body"`),
  nunca el valor. El token no va en URL/query → no entra en access logs de uvicorn/nginx.

## SEC-3 (cripto/revocación) — diseño
El token resuelto se pasa a `verify_token(..., expected_type="refresh")`, `hash_token`,
`is_refresh_token_valid`, `revoke_refresh_token` **sin cambios**. No se re-firma ni se re-emite.

## SEC-5 (no-regresión PWA) — diseño
La rama cookie es la primera de `resolve_refresh_token`, de modo que una petición de la PWA
(solo cookie) se comporta exactamente igual que hoy. La PWA ignora el `refresh_token` del body de
login (invariante verificada en `auth.service.ts`).

## Sources
- [consumes] security-requirements.md (SEC-1..SEC-5), functional-spec.md, contract-summary.md.

## Assumptions & Open Questions
None.
