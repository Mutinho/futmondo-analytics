# Documentación de API — Futmondo Analytics

## API interna (REST, FastAPI)

Superficie: **24 routers** montados en `main.py` bajo `/api/v1/*`, protegidos
por `AuthMiddleware` (Bearer JWT). Rutas públicas (sin auth): `/`, `/health`,
`/auth/*`, `/static/photos/*`, `/docs`.

### Endpoints principales (por área)

| Área | Ruta base | Descripción |
|------|-----------|-------------|
| Auth | `/auth/login`, `/auth/refresh`, `/auth/logout` | login Futmondo, renovar/revocar sesión |
| Usuario | `/api/v1/user/*` | info del usuario, campeonatos (CRUD) |
| Campeonatos | `/api/v1/championships` | lista de campeonatos del usuario |
| Analítica | `/api/v1/analytics/balances`, ... | presupuestos, evolución, estadísticas |
| Mercado | `/api/v1/market/today`, `/api/v1/market/bid` | mercado + puja sugerida; pujar |
| Finanzas | `/api/v1/player-finances/` | finanzas por usuario |
| Sync | `/api/v1/sync/trigger`, `/api/v1/sync/task/{id}` | lanzar sync async; polling |
| Otros | roster, transactions, favorites, sofascore, assistant, matchdays | recursos de datos |
| Salud | `/health` | check de liveness (smoke de release) |

> Contratos de datos detallados y modelos: pendientes (no elaborados a
> profundidad Minimal en scope refactor). Diagramas de secuencia de las
> transacciones principales en `architecture.md` (Interaction Diagrams).

### Hallazgo FR15 — doble montaje de `matchdays`

El **mismo router** de matchdays se incluye **DOS veces** en `main.py`:
`prefix="/api/v1/matchdays"` y `prefix="/v1/matchdays"` (comentario "avoid
redirect loops"). El segundo prefijo `/v1/matchdays` es superficie duplicada a
unificar; **puede tener clientes legacy** — verificar consumo en el
frontend/Sofascore antes de retirarlo (ver `code-quality-assessment.md`).

## APIs externas consumidas

- **Futmondo API** (`futmondo_client.py`): fuente de verdad del juego
  (credenciales por usuario; sesión 12h TTL con re-auth automática).
- **Sofascore API** (`sofascore_client.py`, vía `curl_cffi`): ratings de
  jugadores.
- **Gemini / Groq** (`assistant_service.py`): asistente conversacional.

### Contrato de errores de integración

Módulo `integration_errors.py` con raíz común `IntegrationError` y subtipos
tipados por modo de fallo, **propagados** (no `return None` silencioso).
Recuperable → paso marcado `DEGRADED`; fatal → excepción propagada sin datos a
medias.
