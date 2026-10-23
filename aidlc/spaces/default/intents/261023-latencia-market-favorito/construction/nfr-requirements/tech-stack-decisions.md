# Tech Stack Decisions — Optimización de latencia

## Decisión: sin stack nuevo (reutilización total)

La optimización se implementa **enteramente con el stack existente**; no se
introduce ninguna tecnología, framework ni dependencia nueva. Coste 0 €.

| Área | Selección | Justificación |
|---|---|---|
| Lenguaje/runtime | Python 3.12 (FastAPI existente) | Es el backend actual; sin cambio |
| Acceso a datos | `db_connection.py` existente (`get_db()`, `db.adapt_params`, `db.get_cursor`) | Patrón ya usado por `balances.py` (referencia rápida); SQL parametrizado |
| Capa nueva | Módulo `services/sync_read/` (`favorites_read.py`, `market_read.py`) — SOLO código propio, stdlib | Frontera estrecha testeable; mantiene SQL fuera de router y god-files (C1/BR1.1) |
| Base de datos | Neon PostgreSQL (tier free) existente | Tablas ya sincronizadas; sin esquema nuevo (NFR6) |
| Integración externa (fallback) | Clientes existentes `futmondo_client.py` | Reutilizados tal cual para la ruta viva de fallback |
| Tests | `pytest` + fakes en memoria (`conftest.py`) existentes | Characterization-first; sin red/DB real/credenciales (NFR4) |
| Observabilidad | `logging` stdlib + `fly logs` | Coste 0; sin tooling de pago (Q4-A) |
| Medición de rendimiento | `curl` + script (ya usado en la caracterización) | Sin herramienta de carga nueva (Q2-A) |

## Dependencias nuevas

**Ninguna.** Si en implementación surgiera una necesidad imprevista, sería OSS y
fijada a versión exacta (no se prevé; stdlib suficiente) — regla afirmada.

## Alternativas descartadas

- **Caché TTL por campeonato** (OQ1): descartada por defecto; leer de las tablas
  sincronizadas basta y evita una capa de invalidación extra. Se revisaría solo
  si Performance Validation no alcanzara el objetivo.
- **Tabla de pujas propia / caché en proceso** (OQ2): descartada — las pujas se
  leen en vivo (fuente autoritativa), lo que da coherencia por construcción sin
  riesgo de version-skew; además no existe persistencia de pujas y crearla sería
  cambio de esquema (fuera de alcance).
- **k6/locust, Prometheus/OTel**: descartadas por coste/alcance (Q2-A/Q4-A).
