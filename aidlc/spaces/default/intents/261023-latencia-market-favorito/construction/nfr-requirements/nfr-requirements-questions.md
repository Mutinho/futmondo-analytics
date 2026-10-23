# NFR Requirements — Preguntas

Intent `261023-latencia-market-favorito`. Sólo se preguntan las decisiones NFR
genuinamente abiertas; el resto ya está cuantificado en `requirements.md`
(NFR1–NFR6) y `functional-design` y se arrastra tal cual. Cada ⭐ es la
recomendación.

---

## Q1. Umbral y percentil del objetivo de rendimiento (NFR1)

¿Cómo fijamos el pass/fail del objetivo de latencia (addresing el finding
advisory de Requirements)?

- A. ⭐ **p95 < 0,5 s** para `favorites/my` y para el catálogo de `market/today`
  (parte servida desde sync), medido en caliente (tras warm-up). Se reporta
  además p50 y p99 como contexto. `market/today` incluye la llamada viva de
  pujas, así que su objetivo p95 es **< 0,8 s** (acotado por esa llamada
  irreducible), y el de `favorites/my` es **< 0,5 s** (sin llamada viva). Se
  documenta la distinción.
- B. Un único p95 < 0,5 s para ambos sin distinguir (más estricto en market,
  arriesga falsos rojos por la llamada viva).
- C. Sólo media (p50) < 0,5 s (menos robusto ante colas).
- X. Other (please specify)

[Answer]: A

---

## Q2. Método y entorno de medición (NFR1 / A3)

¿Con qué medimos la aceptación?

- A. ⭐ Mismo método que la caracterización: **N peticiones secuenciales
  autenticadas** (p. ej. 20) con `curl`/script contra producción Fly.io (o
  entorno equivalente), midiendo `time_total`; se calcula p50/p95/p99 y se
  compara contra el umbral de Q1. Warm-up descartado (primera petición). Se
  registra como evidencia en Performance Validation.
- B. Benchmark con herramienta de carga concurrente (k6/locust) — más potente
  pero introduce dependencia/tooling nuevo (roza coste/OSS) y concurrencia que
  hoy no es el problema.
- X. Other (please specify)

[Answer]: A

---

## Q3. Degradación y disponibilidad (Reliability)

¿Qué garantía de fiabilidad fijamos para los endpoints optimizados?

- A. ⭐ **Sin regresión de disponibilidad**: el fallback a la ruta viva en
  sync-miss (BR3.1) y la degradación de pujas a cero si falla `POST
  /1/market/players` con catálogo disponible (BR3.2) garantizan que la respuesta
  **nunca empeora** respecto a hoy (siempre responde y nunca rompe el contrato).
  No se introduce un SLA formal nuevo (coste 0, sin tooling de SLO con
  burn-rate; no aplica al stack Fly.io+Neon free).
- B. Definir un SLA/SLO formal de disponibilidad con ventana y burn-rate
  (requiere tooling de observabilidad de pago/avanzado → choca con coste 0).
- X. Other (please specify)

[Answer]: A

---

## Q4. Observabilidad del cambio (Observability)

¿Qué instrumentación mínima añadimos?

- A. ⭐ **Logging estructurado** de los eventos clave con las herramientas
  gratuitas existentes (`logger` + `fly logs`): `sync-miss fallback`
  (championship_id) y `bid-call degraded` (championship_id), en el nivel
  adecuado (info/warning), **sin credenciales** (NFR5). Sin métricas/tracing
  nuevos de pago. Opcional: log de duración de la lectura desde sync para poder
  verificar el objetivo en producción.
- B. Añadir métricas/tracing distribuido (Prometheus/OTel) — fuera de coste 0 y
  del alcance.
- X. Other (please specify)

[Answer]: A

---

## Q5. Seguridad (Security — artefacto revisado por el adversarial reviewer)

¿Qué postura de seguridad fijamos para la capa nueva?

- A. ⭐ **Sin cambio de superficie de seguridad**: se mantienen auth (Bearer JWT)
  y el scoping por usuario/campeonato (`player_favorites` filtra por `user_id`,
  las pujas son del usuario autenticado). SQL parametrizado en la capa nueva
  (`db.adapt_params`), nunca interpolación. Errores de integración como
  **excepción tipada propagada sin credenciales** en mensaje/`repr`/`exc_info`
  (NFR5, regla afirmada). Sin secretos nuevos; `JWT_SECRET` no-default intacto.
- X. Other (please specify)

[Answer]: A
