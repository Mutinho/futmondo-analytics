# Futmondo Analytics

Aplicación web multi-usuario para gestionar y analizar campeonatos de Futmondo (fantasy football). Permite controlar presupuestos, analizar el mercado, obtener ratings de Sofascore, pujar por jugadores, y calcular finanzas — todo desde una PWA accesible desde iPhone.

## Arquitectura

```
futmondo-analytics/
├── angular-app/          # Frontend Angular 22 + Material 22 (PWA)
├── backend/              # Backend FastAPI (Python 3.12)
├── proxy/                # Nginx reverse proxy (local)
├── docs/                 # Documentación
├── docker-compose.yml    # Orquestación local
└── .env                  # Variables de entorno (no en git)
```

### Stack

| Capa | Tecnología |
|------|-----------|
| Frontend | Angular 22, Material 22, signals, standalone components, PWA |
| Backend | FastAPI, Python 3.12, PyJWT |
| Base de datos | Neon PostgreSQL (serverless, Frankfurt) |
| Integraciones | API Futmondo, API Sofascore (curl_cffi) |
| Deploy | Fly.io (París), GitHub Actions CI/CD |
| Auth | JWT (access token en memoria + refresh token en HttpOnly cookie) |

### Diagrama de producción

```
iPhone/Browser
     │ HTTPS
     ▼
futmondo-app.fly.dev (nginx)
     ├── / → Angular SPA (PWA)
     ├── /api/* → proxy → futmondo-api.fly.dev
     └── /auth/* → proxy → futmondo-api.fly.dev
                              │
                              ▼
                         FastAPI (Python)
                              │
                              ▼
                    Neon PostgreSQL (Frankfurt)
```

## Arrancar en local (Docker)

```bash
cp .env.example .env
# Edita .env con tu DATABASE_URL de Neon

docker compose up --build
# → http://futmondo.localhost
```

## Autenticación

- Los usuarios se autentican con su email/password de Futmondo
- El backend valida contra la API de Futmondo y genera JWT
- **Access token** (1h): en memoria del navegador (nunca en localStorage)
- **Refresh token** (30 días): HttpOnly cookie (inaccesible desde JS)
- Al refrescar la página: el splash recupera la sesión via cookie automáticamente
- Todos los endpoints `/api/v1/*` requieren Bearer token
- Sesión de Futmondo por usuario (12h TTL, re-auth automática)

## Multi-usuario

- Cada usuario tiene sus propios campeonatos auto-detectados al primer login
- Configuración de campeonatos (presupuesto, premios, cláusulas) se obtiene de la API de Futmondo
- Los endpoints usan las credenciales Futmondo del usuario logado (no hay credenciales globales)
- Los datos del campeonato (transacciones, jugadores, standings) son compartidos entre usuarios

## Funcionalidades

### Presupuesto
Tabla de saldos por equipo con detalle de altas/bajas, puja máxima, rendimiento.

### Mercado
Jugadores del computer con puja sugerida (historial), rating Sofascore, tendencia. Modal de puja con min/max validados.

### Sincronización (async)
Sync en background con progreso paso a paso (11 pasos). Incluye: jugadores, transacciones, cláusulas, castigos, dream teams, rendimiento, plantillas, clasificación, odds, phantoms, sofascore. Reconexión al task via localStorage si cierras el modal.

### Finanzas
Cálculo de dinero por usuario: presupuesto + puntos×€ + profit transacciones + dream team + MVP + clasificación (fórmula proporcional de Futmondo) + castigos/bonificaciones.

### Evolución, Estadísticas, Clausulables, Analytics
Gráficos Chart.js, tablas interactivas, analytics avanzado con sub-tabs.

### PWA
Service worker, manifest, Apple meta tags. Instalable como app en iPhone Safari.

### Dark Mode
Toggle en sidebar, persistido en localStorage.

## Deploy (Fly.io)

Ver [docs/DEPLOY.md](docs/DEPLOY.md) para instrucciones completas.

```bash
# Secrets necesarios en Fly.io:
fly secrets set \
  DATABASE_URL="postgresql://..." \
  JWT_SECRET="$(openssl rand -hex 32)" \
  --app futmondo-api
```

## Endpoints principales

| Endpoint | Método | Descripción |
|----------|--------|-------------|
| `/auth/login` | POST | Login con credenciales Futmondo |
| `/auth/refresh` | POST | Renovar access token (cookie) |
| `/auth/logout` | POST | Revocar sesión |
| `/api/v1/user/me` | GET | Info del usuario logado |
| `/api/v1/user/championships` | GET/POST/DELETE | CRUD campeonatos del usuario |
| `/api/v1/championships` | GET | Lista campeonatos del usuario |
| `/api/v1/analytics/balances` | GET | Presupuestos por equipo |
| `/api/v1/market/today` | GET | Mercado + puja sugerida + Sofascore |
| `/api/v1/market/bid` | POST | Pujar por jugador |
| `/api/v1/sync/trigger` | POST | Lanzar sync async (devuelve task_id) |
| `/api/v1/sync/task/{id}` | GET | Polling progreso del sync |
| `/api/v1/player-finances/` | GET | Finanzas por usuario |

## Licencia

MIT
