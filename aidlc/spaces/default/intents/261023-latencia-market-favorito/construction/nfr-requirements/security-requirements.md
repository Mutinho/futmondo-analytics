# Security Requirements — Optimización de latencia

Deriva de inception **NFR5** (errores sin credenciales) y de las reglas de
seguridad afirmadas en memoria. IDs `NFR5.x`.

## Postura: sin cambio de superficie de seguridad

La optimización sólo **cambia la fuente de datos** (leer de Neon sincronizado en
vez de llamar en vivo). No añade endpoints, ni cambia auth, ni toca el contrato.
La superficie de seguridad es la misma que hoy.

## Target Verification Matrix

| ID | Requisito | Criterio pass/fail | Fuente |
|---|---|---|---|
| NFR5.1 | Autenticación intacta | Ambos endpoints siguen exigiendo Bearer JWT (`/api/v1/*`); sin bypass | Q5-A, repo |
| NFR5.2 | Autorización / scoping por usuario | `favorites/my` filtra por `player_favorites(championship_id, user_id)`; las pujas son del usuario autenticado (su token/userid). Un usuario nunca ve favoritos ni pujas de otro | Q5-A, FR1.1 |
| NFR5.3 | SQL parametrizado | Toda consulta de la capa `services/sync_read/` usa parámetros (`db.adapt_params`/placeholders), **nunca** interpolación de strings; previene inyección | Q5-A, C1 |
| NFR5.4 | Errores sin credenciales | El fallo de la ruta viva de fallback **y el fallo de la llamada de pujas `POST /1/market/players`** (BR3.2) se señalan sin credenciales: ni el mensaje, ni el `repr`, ni el `exc_info` incluyen password/token Futmondo — sólo modo de fallo + contexto no sensible (status, endpoint). El fallback usa excepción tipada propagada (nunca `None` silencioso) | NFR5, BR3.2, regla afirmada 2026-09-24 |
| NFR5.5 | Sin secretos nuevos | No se introducen secretos ni dependencias; `JWT_SECRET` no-default en arranque intacto (NFR1.1 del servicio). gitleaks escanea el árbol (incl. tests con fakes) | Q5-A, mandato afirmado |
| NFR5.6 | Privacidad de pujas preservada | `market_today` sigue sin persistir pujas de nadie (privacidad); las pujas sólo se obtienen en vivo para el usuario autenticado. El cambio NO persiste pujas de un usuario en una tabla legible por otros | Q5-A, verificado en código |

## Amenazas consideradas (y por qué no cambian)

- **Inyección SQL**: mitigada por NFR5.3 (parametrización en la capa nueva).
- **Fuga de credenciales en logs/errores**: mitigada por NFR5.4 (regla durable
  afirmada; las excepciones nunca llevan material de credencial).
- **Escalada horizontal (ver datos de otro usuario)**: mitigada por NFR5.2/NFR5.6
  (el scoping por `user_id`/token se preserva; las pujas siguen siendo
  per-usuario y no se persisten compartidas).
- **Nuevos vectores**: ninguno — no hay endpoints, dependencias ni secretos
  nuevos.
