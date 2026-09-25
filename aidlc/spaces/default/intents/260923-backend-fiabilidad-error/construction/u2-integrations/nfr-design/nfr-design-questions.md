# NFR Design — Preguntas · u2-integrations (Integraciones)

Fase Construction, profundidad Standard. El diseño NFR de U2 es en gran parte
una traducción de decisiones ya tomadas (taxonomía recuperable/fatal,
reemplazo transaccional atómico de `team_prizes`, log clave=valor, sin cambio de
infra, coste 0 €). Sólo quedan dos decisiones de diseño concretas que
nfr-requirements dejó abiertas.

Perspectiva inline: arquitecto (lead) + plataforma (adaptada a Fly.io + Neon,
coste 0 €).

---

## Q1 — Valor concreto del timeout por petición de integración (reliability-design)

NFR-perf.1 / NFR-rel.1 fijaron que toda llamada de integración tiene timeout
acotado y dejaron el valor concreto para el diseño. ¿Qué presupuesto fijamos?

- A. **connect ~5 s, read ~30 s** por petición (valores de referencia de la guía
  NFR), aplicados vía el parámetro `timeout` de `requests` (Futmondo) y el
  equivalente de `curl_cffi` (Sofascore). Un exceso lanza
  `IntegrationTimeoutError` (recuperable → `DEGRADED`). Sin retry/backoff.
- B. Un único timeout total más ajustado (p. ej. ~15 s) para acortar el bloqueo
  del cron ante un proveedor lento.
- C. Dejar el valor exacto para code-generation; aquí sólo fijar "timeout
  acotado, no ilimitado" como patrón.
- X. Other (please specify)

[Answer]: A

---

## Q2 — Patrón de resiliencia ante baneo repetido de Sofascore (reliability-design)

Sofascore puede banear la IP (403 → `IntegrationBanError`, fatal). Hoy hay
throttle preventivo (~750 ms). Ante un baneo, ¿qué patrón de diseño adoptamos
además de propagar la excepción tipada?

- A. **Fatal simple**: el baneo aborta limpio el paso sofascore (sin datos a
  medias), se registra `ERROR` estructurado, y el resto del sync continúa con
  los pasos que no dependen de Sofascore. Sin circuit breaker persistente
  (no hay estado entre ejecuciones de cron one-shot; añadirlo sería sobre-
  ingeniería a coste 0 €). El throttle preventivo existente se mantiene como la
  medida anti-baneo.
- B. Añadir un circuit breaker con estado persistente (abrir tras N baneos,
  medio-abierto tras un tiempo) — requiere almacenar estado entre ejecuciones.
- X. Other (please specify)

[Answer]: A

---

## Consolidated Summary Confirmation

- Looks correct
- Request changes

[Answer]: Looks correct
