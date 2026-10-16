# Dependencies — futmondo-analytics

## Dependencias externas (servicios de terceros)

- **API Futmondo** — fuente de verdad de credenciales y datos de campeonato;
  consumida por `futmondo_client.py` (vía `requests`). Acopla la autenticación
  del sistema a la disponibilidad de Futmondo.
- **API Sofascore** — ratings/odds; consumida por `sofascore_client.py` vía
  **`curl_cffi`** (impersonación de navegador para sortear bloqueos).
- **LLM Gemini** (`google-genai`) con **fallback a Groq** (`groq`) — asistente IA
  (`assistant/infrastructure/llm_adapter.py`).
- **Neon PostgreSQL** — persistencia (driver `psycopg2-binary`).
- **Fly.io** — hosting (dos apps + cron one-shot). **GitHub Actions** — CI/CD.
  Todo dentro de tiers gratuitos (restricción coste 0 €).

## Dependencias de librería

Versiones completas en `technology-stack.md`. Resumen de las de mayor impacto:

- **Frontend**: ecosistema Angular 22 (`@angular/*` `^22.2.1`), `@angular/material`
  + `@angular/cdk` (DOM), `chart.js`/`ng2-charts` (`<canvas>`), `marked`, `rxjs`.
- **Backend**: `fastapi`/`uvicorn`/`pydantic`, `requests`, `curl_cffi`, `PyJWT`,
  `psycopg2-binary`, `google-genai`/`groq`.

## Dependencias cruzadas internas (entre paquetes)

- **`angular-app` → `backend`**: acople único por contrato HTTP `/api/v1/*` +
  `/auth/*` (12 servicios Angular ↔ 59 operaciones FastAPI). No hay código
  compartido entre builds (no monorepo tooling).
- **`cron` → `backend`**: comparte Dockerfile y ejecuta `backend/scripts/*`;
  depende del código de servicios del backend.
- **`proxy` → `angular-app` + `backend`**: enruta tráfico local (sólo
  `docker-compose`).

## Dependencias internas dentro del backend

- **`api/v1/endpoints/` → `services/` y `db_connection`**: la capa HTTP delega en
  servicios; 17 endpoints además ejecutan SQL directo (SQL-en-router), acoplando
  persistencia y HTTP (deuda; ver `code-quality-assessment.md`).
- **`services/` → `db_connection` → Neon**: `data_manager`, `data_sync_service`,
  `analytics`, `assistant`, `photo_service` persisten vía `db_connection`
  (incluye el `adapt_params()` `? → %s` heredado).
- **`services/` → `external-clients`**: `data_sync_service`/`task_service`
  orquestan `futmondo_client`/`sofascore_client`; `assistant` usa `llm_adapter`.
- **`auth/` → API Futmondo + Neon**: valida credenciales y persiste sesión/token.

## Relevancia para el intent (viabilidad nativa)

Una app nativa (NativeScript + Angular) reutilizaría las **dependencias de
servicio/datos** (mismo contrato HTTP al backend) pero **no** las dependencias de
presentación DOM (`@angular/material`, `@angular/cdk`, `chart.js`/`ng2-charts`,
service worker/PWA), que requieren equivalentes nativos. Detalle en
`code-quality-assessment.md`.
