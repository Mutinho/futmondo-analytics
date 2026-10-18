# Units of Work — F1: Login nativo end-to-end

> Fase: inception (units-generation). Unidades de trabajo para la fase de construcción, con su
> tipo (`kind`) y dependencias (`depends_on`). Idioma: castellano; tokens técnicos (claves/enums
> YAML, identificadores) verbatim en inglés.

## Unidades

```yaml
units:
  - name: backend-refresh-transport
    kind: service
    depends_on: []
  - name: ios-network-client
    kind: library
    depends_on: [backend-refresh-transport]
  - name: ios-native-auth
    kind: ui
    depends_on: [ios-network-client]
```

## Descripción de las unidades

### `backend-refresh-transport` (`service`) — [F1-U1, C6, FR-4, FR-9]
Ajuste aditivo del backend FastAPI para el transporte del refresh token:
- `POST /auth/login` devuelve el refresh token también en el body.
- `POST /auth/refresh` y `POST /auth/logout` aceptan el refresh token por cookie **O** body/header
  (precedencia cookie-first).
- Tests `pytest` que aseveran el efecto en ambos canales (cookie + body/header), incl. revocación.
- characterization-first; sin ampliar god-files ni el patrón SQL-en-router.
- **Sin dependencias** (es la base que desbloquea el transporte nativo).

### `ios-network-client` (`library`) — [F1-U2, C1, FR-7]
Capa de red Swift sobre `URLSession`: base URL, JSON `Codable`, inyección de `Bearer`, errores
tipados; llamada de humo a `GET /api/v1/user/me`. **Depende de** `backend-refresh-transport`
(necesita el contrato de transporte estabilizado).

### `ios-native-auth` (`ui`) — [F1-U3, C2/C3/C4/C5, FR-1,FR-2,FR-3,FR-5,FR-6,FR-8]
Auth nativa completa: `KeychainStore`, `AuthService` (login/refresh/bootstrap/logout, access en
memoria, reintento único, revocación pendiente), `AuthViewModel`, `LoginView`/`SplashView` con
UX nativa. **Depende de** `ios-network-client`.

## DAG (camino lineal)

`backend-refresh-transport` → `ios-network-client` → `ios-native-auth`.

## Notas para etapas siguientes (reviewer de arquitectura)

- **`ios-native-auth` es la unidad de mayor alcance** (6 FR, 6 US, C2–C5). Su cohesión es alta y
  partirla introduciría acoplamiento intra-auth; se mantiene entera. **Nota para
  delivery-planning**: vigilar su tamaño de bolt; valorar sub-batching si la planificación lo
  requiere (opcional).
- **Precedencia cookie-first**: `contract-design` debe **ratificar** explícitamente que, cuando
  llegan ambos canales, se prefiere cookie (compat PWA) y body/header es el fallback nativo; y
  confirmar que el canal body/header de `backend-refresh-transport` satisface lo que
  `ios-network-client`/`ios-native-auth` consumen para FR-5.

## Sources

- [consumes] components.md, decisions.md, requirements.md, stories.md.
- [backlog] intent-backlog de F1 (F1-U1/U2/U3).

## Assumptions & Open Questions

None.
