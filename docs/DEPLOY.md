# Despliegue en Fly.io

## Requisitos previos

1. Cuenta en [Fly.io](https://fly.io) (registro gratuito)
2. CLI de Fly instalado: `curl -L https://fly.io/install.sh | sh`
3. Login: `fly auth login`

---

## Primer despliegue (setup inicial)

### 1. Crear las apps en Fly.io

```bash
# Backend
cd backend
fly apps create futmondo-api --machines

# Frontend
cd ../angular-app
fly apps create futmondo-app --machines
```

### 2. Configurar secrets del backend

```bash
cd backend
fly secrets set \
  FUTMONDO_EMAIL="tu-email@ejemplo.com" \
  FUTMONDO_PASSWORD="tu-password" \
  DATABASE_URL="postgresql://user:pass@host/db?sslmode=require" \
  BASE_URL="https://api.futmondo.com" \
  CHAMPIONSHIP_ID="592416daa3a2dd871a7a9956" \
  --app futmondo-api
```

### 3. Desplegar backend

```bash
cd backend
fly deploy
```

Verificar: `https://futmondo-api.fly.dev/health`

### 4. Desplegar frontend

```bash
cd angular-app
fly deploy
```

Verificar: `https://futmondo-app.fly.dev`

---

## Despliegue automático (CI/CD)

El workflow `.github/workflows/fly-deploy.yml` despliega automáticamente al hacer push a `main`.

### Configurar el token en GitHub:

1. Generar token: `fly tokens create deploy -x 999999h`
2. Ir a GitHub → repo → Settings → Secrets → Actions
3. Crear secret: `FLY_API_TOKEN` con el valor del token

---

## URLs de producción

| Servicio | URL |
|----------|-----|
| Frontend | https://futmondo-app.fly.dev |
| Backend API | https://futmondo-api.fly.dev |
| Health check | https://futmondo-api.fly.dev/health |

---

## PWA en iPhone

1. Abrir `https://futmondo-app.fly.dev` en Safari
2. Pulsar el icono de compartir (cuadrado con flecha)
3. Seleccionar "Añadir a pantalla de inicio"
4. La app se instalará como "Futmondo" con icono propio

---

## Comandos útiles

```bash
# Ver logs en tiempo real
fly logs --app futmondo-api
fly logs --app futmondo-app

# Estado de las máquinas
fly status --app futmondo-api
fly status --app futmondo-app

# Escalar (si necesitas más RAM)
fly scale memory 512 --app futmondo-api

# SSH al contenedor
fly ssh console --app futmondo-api

# Reiniciar
fly apps restart futmondo-api
```

---

## Arquitectura en producción

```
iPhone/Browser
     │
     ▼ (HTTPS)
futmondo-app.fly.dev (nginx)
     │
     ├─ / → Angular SPA (static files)
     │
     └─ /api/* → proxy → futmondo-api.fly.dev
                              │
                              ▼
                         FastAPI (Python)
                              │
                              ▼
                    Neon PostgreSQL (Frankfurt)
```

---

## Notas

- **Free tier**: 3 máquinas gratis. Usamos 2 (backend + frontend). Siempre activas (min_machines=1).
- **Región**: Madrid (mad) — mínima latencia desde España.
- **HTTPS**: Automático con certificado de Fly.io, sin configuración extra.
- **Dominio custom** (opcional): `fly certs add tudominio.com --app futmondo-app`
