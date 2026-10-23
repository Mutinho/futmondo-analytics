# Requirements Analysis — Preguntas de clarificación

Intent: `261023-latencia-market-favorito` — optimizar latencia de
`GET /api/v1/market/today` (~1,6 s) y `GET /api/v1/favorites/my` (~3,4 s).

Contexto de la ingeniería inversa (ya fijado, NO se pregunta): la latencia es
proporcional a las **llamadas HTTP en vivo a Futmondo por request**, no a Neon.
`balances` (~0,4 s) es el patrón rápido: 1 llamada viva + lecturas de Neon
sincronizado. `favorites/my` hace la pesada `get_championship_players` (baja la
lista completa de jugadores solo para filtrar favoritos). `market/today` hace 1
llamada viva siempre para las **pujas del usuario**. Ya existe
`DataSyncService` que pre-sincroniza catálogo de jugadores, stats, standings,
etc. en Neon. Restricciones durables: coste 0 €, NO ampliar god-files
(`data_sync_service.py`, `data_manager_v2.py`) ni SQL-en-router; capa nueva
estrecha y testeable; characterization-first; gate de CI verde.

Responde cada `[Answer]:` con la letra. Recomendación marcada con ⭐.

---

## A. Objetivo de latencia

- A. **<0,5 s** para ambos endpoints en la mayoría de requests (percentil alto,
  p. ej. p95), como pedía el intent, usando como patrón `balances`. ⭐
- B. Solo "notablemente más rápido" sin umbral numérico.
- C. Otro umbral (especifícalo).
- X. Other (please specify)

[Answer]: A

---

## B. Tolerancia de staleness (datos servidos desde Neon pre-sincronizado)

Servir desde datos sincronizados implica que pueden estar algo desactualizados
respecto a Futmondo en vivo (hasta la última sincronización).

- A. Aceptable que **valores/stats/catálogo** (valor, tendencia, puntos, media,
  rating) reflejen la **última sincronización** (minutos/horas), como ya ocurre
  con balances; el usuario entiende que los datos se refrescan con la sync. ⭐
- B. Los datos deben ser siempre en vivo (entonces no se puede optimizar sin
  cambiar el enfoque).
- X. Other (please specify)

[Answer]: A

---

## C. Las PUJAS del usuario en `market/today` (dato sensible a frescura)

Hoy `market/today` hace 1 llamada viva **siempre** para traer las pujas activas
del usuario (la caché las quita por privacidad). Es parte de la lentitud.

- A. Las pujas pueden servirse desde un estado cacheado/propio **invalidado tras
  pujar/cancelar** (el backend ya conoce esos eventos), evitando la llamada viva
  en la carga normal. El saldo/importe de pujas debe quedar coherente tras una
  operación. ⭐
- B. Mantener SIEMPRE la llamada viva para las pujas (prioriza frescura de pujas
  sobre latencia); se optimiza solo el resto.
- X. Other (please specify)

[Answer]: A

---

## D. Qué hacer si faltan datos sincronizados (sync-miss)

Si un campeonato aún no tiene datos sincronizados en Neon (p. ej. primer uso):

- A. **Fallback** a la ruta en vivo actual (más lenta pero correcta) cuando no
  haya datos sincronizados; el endpoint nunca devuelve vacío por falta de
  caché. Se registra para observabilidad. ⭐
- B. Devolver vacío/estado "sincronizando" y que el cliente reintente.
- X. Other (please specify)

[Answer]: A

---

## E. Estrategia preferida (read-from-sync vs caché TTL)

- A. Preferir **read-from-sync** (leer de las tablas Neon que `DataSyncService`
  ya rellena), que es el patrón probado de `balances`; añadir caché TTL por
  campeonato solo si algún dato no está sincronizado y conviene memizarlo. El
  diseño fino lo decide Functional Design. ⭐
- B. Caché TTL por campeonato como mecanismo principal (memoizar la respuesta
  actual N minutos).
- X. Other (please specify)

[Answer]: A

---

## F. Alcance (qué NO tocar)

- A. Alcance **solo** a `market/today` y `favorites/my` (y la capa de lectura
  nueva); NO tocar `balances` (ya rápido), NO cambiar `DataSyncService` más allá
  de leer lo que ya sincroniza, NO cambiar el contrato de respuesta, NO tocar
  CI/despliegue más allá de pasar el gate. ⭐
- B. Incluir también otros endpoints lentos (especifícalos).
- X. Other (please specify)

[Answer]: A
