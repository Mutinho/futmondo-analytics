# Stakeholder Map — F3 Mercado (app nativa iOS)

## Stakeholders

| Stakeholder | Rol | Interés / necesidad | Impacto de F3 |
|---|---|---|---|
| **Usuario/propietario (mánager)** | Usuario final y dueño del producto | Ver el mercado y pujar desde el iPhone con la misma fluidez y tema que el resto de la app nativa | Alto — gana la pantalla de mayor valor accionable (fichar) en nativo |
| **Jugadores del mismo campeonato** | Terceros afectados | Compiten por los mismos jugadores del computer; una puja realizada desde la app nativa cambia el estado compartido del campeonato | Medio — una puja/cancelación nativa tiene el mismo efecto real que desde la PWA |
| **Backend Futmondo Analytics (FastAPI)** | Sistema proveedor | Sirve `/api/v1/market/*`; no cambia por F3 | Nulo en contrato — sólo nuevo consumidor nativo |
| **API Futmondo (externa)** | Sistema aguas abajo | El backend propaga la puja/cancelación a Futmondo con las credenciales del usuario | Indirecto — la escritura nativa llega a Futmondo igual que la web |
| **API Sofascore (externa)** | Sistema aguas abajo | Provee las estadísticas del detalle de jugador (endpoint aparte) | Indirecto — el detalle Sofascore está **dentro de alcance** (Q3=A), así que el cliente nativo consume ese endpoint aparte además de `/today` |
| **Equipo de desarrollo (este flujo AI-DLC)** | Ejecutor | Construir la sección reutilizando `FutmondoKit` + `DesignSystem`, con rigor anti-hueco-WSL | Alto — primera escritura del cliente nativo |

## Decisiones que requieren al propietario

- **Q1 — Alcance de escritura**: incluir pujar + cancelar en F3, o limitar a
  lectura + orden. Es la decisión de mayor impacto: habilita la primera
  operación de escritura del cliente nativo, con efecto real sobre el campeonato
  compartido (afecta a los demás jugadores) y mayor superficie de
  seguridad/riesgo que F1/F2.
- **Q2 — Campos de la card** y **Q3 — detalle Sofascore**: afinan el alcance de
  la UI y el consumo de un segundo endpoint externo.

## Notas de seguridad / riesgo (para arrastrar a diseño)

- La escritura usa la **sesión autenticada** ya establecida por F1
  (`AuthService`, refresh token en Keychain, nunca en claro). F3 no introduce
  almacenamiento de credenciales nuevo.
- Una puja es una acción con **efecto económico real** en el campeonato: la UI
  debe confirmar/validar el importe (mín = precio de mercado, máx = límite
  disponible) y dar señal clara de éxito/error, sin dejar la pantalla en estado
  ambiguo (refresco tras la acción).
