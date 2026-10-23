# Requirements — Optimización de latencia de market/today y favorites/my

Intent: `261023-latencia-market-favorito` · Scope: `refactor` (plan
`optimizar-latencia-market-favoritos`) · Fase: INCEPTION.

## Intent analysis

Reducir la latencia de `GET /api/v1/market/today` (~1,6 s) y
`GET /api/v1/favorites/my` (~3,4 s) sirviéndolos mayoritariamente desde datos
**pre-sincronizados en Neon** (patrón ya probado por `/api/v1/analytics/balances`,
~0,4 s) en vez de hacer llamadas HTTP **en vivo** a Futmondo/Sofascore en cada
request. Causa raíz (reverse-engineering): la latencia es proporcional al número
de llamadas vivas por request. El objetivo es que la mayoría de requests
respondan en **<0,5 s** sin cambiar el **contrato de respuesta** que consumen el
frontend Angular y el cliente nativo iOS. Evidencia:
`knowledge/aidlc-shared/backend-latency-market-favorites.md` y el codeKB.

## Functional requirements

### FR1 — `favorites/my` desde datos sincronizados
- FR1.1 Servir `GET /api/v1/favorites/my` leyendo el **catálogo/valores de
  jugadores desde Neon** (lo que `DataSyncService` ya sincroniza: players /
  player_championship_stats / standings / sofascore_cache), **eliminando la
  llamada viva pesada** `get_championship_players` (que hoy descarga la lista
  completa solo para filtrar favoritos).
- FR1.2 El filtro de favoritos sigue siendo el `SELECT` barato sobre
  `player_favorites` del usuario/campeonato.
- FR1.3 El **orden** se preserva: `position_order` asc y luego `value` desc.

### FR2 — `market/today` sin llamada viva en la carga normal
- FR2.1 Servir `GET /api/v1/market/today` desde la caché/datos sincronizados ya
  existentes para el catálogo de mercado, **sin** la llamada viva por defecto.
- FR2.2 Las **pujas activas del usuario** (que hoy motivan la llamada viva
  siempre) se sirven desde un **estado propio/cacheado** del backend,
  **invalidado tras** `POST /market/bid` y `POST /market/cancelbid`, de modo que
  `user_info` (balance, `active_bids_total`, `active_bids_count`,
  `available_for_bids`) quede **coherente tras una operación**.

### FR3 — Contrato de respuesta intacto
- FR3.1 Las respuestas de ambos endpoints mantienen **exactamente** su forma y
  campos actuales (documentados en el codeKB): `market/today` → `success`,
  `championship_id`, `total_in_market`, `computer_players`, `players[]` (~30
  campos) y `user_info{...}`; `favorites/my` → `players[]` (con todos sus
  campos) y `total`. Ningún consumidor (Angular, iOS) debe requerir cambios.

### FR4 — Fallback en sync-miss
- FR4.1 Si un campeonato **no tiene datos sincronizados** suficientes en Neon, el
  endpoint hace **fallback a la ruta en vivo** actual (correcta aunque más
  lenta); nunca devuelve vacío por ausencia de caché.
- FR4.2 El fallback se **registra** (log/observabilidad) para poder detectar
  campeonatos sin sincronizar.

### FR5 — Capa de lectura nueva, estrecha y testeable
- FR5.1 La lógica de lectura-desde-sync (y la memoización TTL si se usa) vive en
  una **capa/función nueva estrecha y testeable**, NO ampliando los god-files
  `data_sync_service.py` ni `data_manager_v2.py`, ni el patrón SQL-en-router.
- FR5.2 Reutiliza lo que `DataSyncService` ya sincroniza; **no** cambia la
  sincronización más allá de **leer** lo ya sincronizado.

## Non-functional requirements

- NFR1 (Rendimiento) `market/today` y `favorites/my` responden en **<0,5 s** en
  la mayoría de requests (objetivo p95), medido como en la caracterización
  (ttfb/total contra el entorno), tomando `balances` (~0,4 s) como referencia.
  La magnitud exacta y el método de medición se detallan en NFR Requirements.
- NFR2 (Frescura/staleness) Es aceptable que valores, stats y catálogo reflejen
  la **última sincronización** (como balances); las **pujas** del usuario, en
  cambio, deben ser **coherentes tras pujar/cancelar** (FR2.2).
- NFR3 (Coste) Coste 0 €: solo Neon free / Fly.io free; sin dependencias de pago
  (o OSS fijada a versión exacta si fuera imprescindible — no se prevé).
- NFR4 (Testabilidad / characterization-first) **Caracterizar (congelar con
  tests) el comportamiento actual** de ambos endpoints ANTES de cambiarlo; los
  tests usan dobles/fakes en memoria (patrón `conftest.py`), sin red, sin DB
  real ni credenciales. Mantener el gate de CI bloqueante (gitleaks + ruff +
  pytest + pip-audit) en verde; el piso de cobertura sólo sube.
- NFR5 (Errores) El fallo de integración externa se señala como **excepción
  tipada propagada** (nunca `None` silencioso), sin credenciales en el mensaje.
- NFR6 (Compatibilidad) Sin cambios de esquema de API ni de contrato; sin
  migraciones destructivas; reutilizar las tablas ya sincronizadas.

## Constraints

- C1 **NUNCA ampliar los god-files** `data_sync_service.py` (~15 KB) ni
  `data_manager_v2.py` (~33 KB), ni el patrón SQL-en-router; el código nuevo va
  tras una capa/función estrecha testeable.
- C2 **Contrato de respuesta inmutable** (Angular + iOS lo consumen tal cual).
- C3 Coste 0 €; pasar el gate de CI bloqueante antes de fusionar a `main`.
- C4 No tocar `balances` (ya rápido) ni CI/despliegue más allá de pasar el gate.

## Assumptions

- A1 Los datos que necesita `favorites/my` (valor, tendencia, puntos, media,
  rating, titularidad, posiciones) están disponibles en las tablas que
  `DataSyncService` ya rellena; Functional Design confirmará el mapeo exacto
  campo→tabla. (Razón: el reverse-engineering los identificó como sincronizados.)
- A2 El backend conoce los eventos de puja/cancelación (endpoints `bid`/
  `cancelbid`), por lo que puede invalidar el estado de pujas cacheado (FR2.2).
- A3 La medición de aceptación se hará contra un entorno comparable al de la
  caracterización (producción Fly.io o equivalente), con el mismo método.

## Out of scope

- O1 Cambiar el **contrato** de respuesta de los endpoints.
- O2 Ampliar o rediseñar `DataSyncService`/`data_manager_v2` (solo se lee de lo
  ya sincronizado).
- O3 Optimizar otros endpoints (`balances` ya es rápido; el resto queda fuera).
- O4 Cambios de CI/CD o despliegue más allá de pasar el gate existente.
- O5 Cliente nativo iOS / frontend Angular: no se tocan (ya mitigan la espera
  con skeleton + caché; el objetivo es eliminar la causa en el backend).

## Open questions

- OQ1 ¿Conviene una caché TTL por campeonato como complemento del read-from-sync
  para el catálogo de mercado, o basta con leer de las tablas sincronizadas?
  (Decisión fina de Functional Design; por defecto read-from-sync.)
- OQ2 Mecanismo exacto de almacenamiento/invalidación del estado de pujas del
  usuario (tabla propia vs. caché en proceso con TTL corto) — Functional Design.
