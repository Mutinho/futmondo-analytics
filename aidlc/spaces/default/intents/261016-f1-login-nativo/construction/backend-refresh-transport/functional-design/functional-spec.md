# Functional Spec — `backend-refresh-transport` (Bolt 1 de F1)

> Fase: construcción (functional-design). Especificación funcional del ajuste aditivo del
> transporte del refresh token. Idioma: castellano; tokens técnicos verbatim en inglés.

## Objetivo

Permitir que un cliente sin cookies de navegador (la app iOS nativa) complete el ciclo
login → refresh → logout, **sin romper** el canal cookie `HttpOnly` que usa la PWA Angular. Cambio
aditivo y acotado en `backend/app/auth/routes.py` (+ `models.py` para los bodies opcionales).

## Cambios por endpoint

### `POST /auth/login`
- **Antes**: fija cookie `HttpOnly` y devuelve un `dict` crudo sin `refresh_token`.
- **Después**: fija la cookie **igual** y **añade la clave `refresh_token`** al mismo `dict`
  (BR2). El resto del body no cambia; no se migra a modelo Pydantic.
- **Efecto verificable**: la response trae `refresh_token`; la cookie sigue presente.

### `POST /auth/refresh`
- **Firma objetivo** (evita el 422 de la PWA — Critical):
```
@router.post("/refresh")
async def refresh(
    request: Request,
    futmondo_refresh_token: Optional[str] = Cookie(default=None),
    x_refresh_token: Optional[str] = Header(default=None, alias="X-Refresh-Token"),
    body: Optional[RefreshBodyOptional] = None,   # body OPCIONAL -> sin body no hay 422
):
    token = futmondo_refresh_token or x_refresh_token or (body.refresh_token if body else None)
    if not token: raise HTTPException(401, "No refresh token")
    ...  # resto SIN cambios (verify_token, is_refresh_token_valid, nuevo access token)
```
- **Precedencia** cookie → header → body (BR1). El resto del cuerpo del handler no cambia.
- **Efecto verificable**: refresh por cookie → 200 (como hoy, **sin** enviar body: no 422);
  por header → 200; por body → 200; sin token por ningún canal → 401.

### `POST /auth/logout`
- **Firma objetivo**: añade `x_refresh_token: Header(default=None, alias="X-Refresh-Token")` y
  `body: Optional[LogoutBodyOptional] = None`; resuelve el token por la misma precedencia (BR1)
  y revoca por hash (BR3, BR6); sigue borrando la cookie (inocuo para el cliente nativo, que no
  la usa).
- **Efecto verificable**: logout por cualquier canal → token revocado (refresh posterior con ese
  token da 401).

### Nota sobre el borde cookie-revocada + body-válido (Minor del review)
La precedencia es por **presencia**, no por validez: si llega una cookie (aunque esté revocada) y
también un body con token válido, **gana la cookie** y el endpoint responde 401 (token revocado).
Es el comportamiento correcto y determinista: un cliente nativo **no envía cookie**, así que nunca
cae en este borde; la PWA solo envía cookie. Se documenta explícitamente para que el test lo fije.

## Flujo (cliente nativo)

```mermaid
sequenceDiagram
    participant App as App iOS
    participant API as FastAPI
    App->>API: POST /auth/login {email,password}
    API-->>App: 200 { access_token, refresh_token, ... }
    Note over App: access en memoria; refresh en Keychain
    App->>API: POST /auth/refresh (X-Refresh-Token o body)
    API-->>App: 200 { access_token }
    App->>API: POST /auth/logout (X-Refresh-Token o body)
    API-->>App: 200 { success:true }  (token revocado)
```

Fallback de texto: la app hace login y recibe access+refresh en el body; guarda el refresh en
Keychain; refresca enviando el refresh por header/body; cierra sesión enviando el refresh por
header/body, que lo revoca.

## Tests (pytest, aseveran el efecto — ambos canales)

1. `login` devuelve `refresh_token` en el body **y** fija la cookie `Set-Cookie`
   `futmondo_refresh_token` (no-regresión).
2. `refresh` por **cookie, sin body** → 200 (comportamiento PWA actual; **y** aserta que NO es 422
   — cierra el Critical del body opcional).
3. `refresh` por **header** `X-Refresh-Token` (sin cookie) → 200 con nuevo access token.
4. `refresh` por **body** `{refresh_token}` (sin cookie) → 200.
5. `refresh` **sin token** por ningún canal → 401.
6. `logout` por **header** y por **body** revoca → un `refresh` posterior con ese token da 401
   (dos casos).
7. **Precedencia observable**: se emiten dos refresh tokens válidos y distintos, T_cookie y
   T_body, para dos usuarios distintos (U_cookie, U_body); se llama a `refresh` con la cookie=
   T_cookie y el body=T_body a la vez; se decodifica el access token devuelto y se **asevera que
   su `sub` == U_cookie** (ganó la cookie), no U_body. Así el test observa el canal ganador y no
   puede pasar de forma trivial.
8. **Borde cookie-revocada + body-válido**: cookie con token **revocado** + body con token
   válido → **401** (gana la cookie por presencia, BR1), aseverando el status y que el token del
   body **no** fue aceptado.

Todos con fakes in-memory (patrón `conftest.py`), sin red, sin BD real, sin tokens reales
(generados en el test con la cripto real sobre un `JWT_SECRET` efímero del fixture).

## Alcance y límites

- Solo `auth/routes.py` (+ modelos de body opcionales en `auth/models.py`). No se amplían
  god-files ni el patrón SQL-en-router. No se toca la cripto.
- `GET /api/v1/user/me` no se modifica (ya valida Bearer por header).

## Sources

- [consumes] contract-summary.md, components.md (C6), requirements.md (FR-4, FR-9, NFR-1),
  rules.md, entities.md.
- [code] `auth/routes.py`, `auth/models.py`, `jwt_utils.py`, `token_store.py`,
  `test_auth_characterization.py`.

## Assumptions & Open Questions

None.
