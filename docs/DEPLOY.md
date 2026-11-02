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

# (El frontend NO se crea en Fly: se publica en Cloudflare Pages — ver más abajo.)
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
  JWT_SECRET="$(openssl rand -hex 32)" \
  FUTMONDO_CRED_KEY="$(python -c 'from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())')" \
  --app futmondo-api
```

> **`FUTMONDO_CRED_KEY` (durabilidad de sesión — u1-durable-session).** Clave
> simétrica Fernet (base64 url-safe, 32 bytes) que cifra en reposo el handle de
> re-autenticación de Futmondo, de modo que la sesión sobrevive a un reinicio
> **sin** persistir jamás la contraseña en claro (FR5.1 / NFR1). Genérala con
> `Fernet.generate_key()` y guárdala SOLO como secret de Fly.io — **nunca** en el
> repositorio ni en el workflow. Si no está configurada, el backend arranca
> igual pero no puede rehidratar sesiones tras un reinicio: el primer uso
> devuelve un **401 accionable** (re-login) en lugar de un 403 opaco. Rotarla
> invalida los handles cifrados existentes y obliga a un nuevo login por usuario.

### 3. Desplegar backend

```bash
cd backend
fly deploy
```

Verificar: `https://futmondo-api.fly.dev/health`

### 4. Desplegar frontend (Cloudflare Pages)

El frontend ya **no** se despliega en Fly. Se publica en Cloudflare Pages
(gratis). Ver la sección "Despliegue del frontend en Cloudflare Pages" más
abajo para la configuración de build.

Verificar: `https://<tu-proyecto>.pages.dev`

---

## Despliegue automático (CI/CD)

El workflow `.github/workflows/fly-deploy.yml` despliega automáticamente al hacer push a `main`.

> **Pendiente tras migrar el frontend a Cloudflare Pages:** el workflow aún
> contiene un job `deploy-frontend` (`flyctl deploy` en `angular-app/`). Al
> publicar el frontend en Cloudflare Pages ese job sobra. Opciones:
> - Eliminar el job `deploy-frontend` (y su `needs:` en `smoke-test`), dejando
>   solo `verify` + `deploy-backend`. Cloudflare Pages se encarga de su propio
>   despliegue al detectar el push vía su integración Git.
> - O dejarlo hasta validar Cloudflare Pages y retirarlo después.
> Mientras exista, seguirá desplegando (y manteniendo activa) la app
> `futmondo-app` en Fly — bórrala (`fly apps destroy futmondo-app`) cuando
> confirmes que Cloudflare Pages funciona, para que deje de contar coste.

### Configurar el token en GitHub:

1. Generar token: `fly tokens create deploy -x 999999h`
2. Ir a GitHub → repo → Settings → Secrets → Actions
3. Crear secret: `FLY_API_TOKEN` con el valor del token

---

## URLs de producción

| Servicio | URL |
|----------|-----|
| Frontend | https://&lt;tu-proyecto&gt;.pages.dev (Cloudflare Pages) |
| Backend API | https://futmondo-api.fly.dev |
| Health check | https://futmondo-api.fly.dev/health |

---

## PWA en iPhone

1. Abrir `https://<tu-proyecto>.pages.dev` en Safari
2. Pulsar el icono de compartir (cuadrado con flecha)
3. Seleccionar "Añadir a pantalla de inicio"
4. La app se instalará como "Futmondo" con icono propio

---

## Comandos útiles

```bash
# Ver logs en tiempo real
fly logs --app futmondo-api

# Estado de las máquinas
fly status --app futmondo-api

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
futmondo-app.pages.dev (Cloudflare Pages — estático, gratis)
     │
     ├─ / → Angular SPA (static files, CDN global)
     │
     └─ /api/*, /auth/* → proxy (rewrite 200) → futmondo-api.fly.dev
                                                     │
                                                     ▼ (auto-stop: se duerme sin tráfico)
                                                FastAPI (Python) en Fly.io
                                                     │
                                                     ▼
                                            Neon PostgreSQL (Frankfurt)
```

El proxy del frontend lo definen `angular-app/public/_redirects` (reescritura
`200` → same-origin, sin CORS) y `angular-app/public/_headers` (seguridad +
caché). Reemplazan el `nginx.prod.conf` que se usaba cuando el frontend vivía
en Fly.

---

## Coste y optimización (objetivo ~0€)

> **Importante: Fly.io ya NO tiene free tier.** El plan es *pay-as-you-go*. El
> coste dominante es el tiempo de cómputo de máquinas encendidas (segundos-core).
> Dos máquinas `shared-cpu-1x:256MB` activas 24/7 ≈ **$5/mes**.

Para dejar la factura cerca de 0€ sin perder funcionalidad:

1. **Frontend fuera de Fly → Cloudflare Pages (gratis).** Elimina una máquina
   entera. Ver "Despliegue del frontend en Cloudflare Pages" más abajo.
2. **Backend en Fly con auto-stop.** En `backend/fly.toml`:
   ```toml
   [http_service]
     auto_stop_machines  = "stop"   # se detiene sin tráfico
     auto_start_machines = true       # arranca en la 1ª petición
     min_machines_running = 0         # 0 máquinas en reposo
   ```
   La máquina se duerme sin tráfico y arranca bajo demanda (cold start ~2–5s en
   la primera petición). La sesión durable se rehidrata vía `FUTMONDO_CRED_KEY`,
   así que un reinicio no fuerza re-login mientras la clave esté configurada.

---

## Despliegue del frontend en Cloudflare Pages

1. **Conectar el repo** en el dashboard de Cloudflare Pages
   (Workers & Pages → Create → Pages → Connect to Git).
2. **Configuración de build:**
   | Ajuste | Valor |
   |---|---|
   | Framework preset | Angular (o "None") |
   | Build command | `cd angular-app && npm ci && npx ng build --configuration=production` |
   | Build output directory | `angular-app/dist/angular-app/browser` |
   | Root directory | *(raíz del repo)* |
   | Variable `NODE_VERSION` | `22.22.3` (coincide con `.nvmrc`; el CLI de Angular exige ≥ 22.22.3) |
3. **Deploy.** Cloudflare asigna `https://<proyecto>.pages.dev`. El `_redirects`
   ya enruta `/api/*` y `/auth/*` al backend en Fly; no hay que tocar el código
   Angular (usa rutas relativas).
4. **(Opcional) dominio propio:** añadir en Pages → Custom domains.

> El build local en este repo puede fallar si tu Node del sistema es < 22.22.3;
> Cloudflare usa su propio Node según `NODE_VERSION`/`.nvmrc`, así que el build
> en CF Pages no se ve afectado.

### CORS (normalmente no hace falta)

El proxy `_redirects` usa reescritura `200`, por lo que el navegador ve todo
como **same-origin** (`*.pages.dev`) y **no se dispara CORS**. Solo si llamas al
API directamente al dominio de Fly desde otro origen (p. ej. la app iOS o
pruebas), añade ese origen como secret:

```bash
fly secrets set EXTRA_CORS_ORIGIN="https://<tu-proyecto>.pages.dev" --app futmondo-api
```

El backend ya lee `EXTRA_CORS_ORIGIN` y lo añade a la whitelist (`app/main.py`).

---

## Notas

- **Sin free tier en Fly**: el coste es *pay-as-you-go*; optimizado con auto-stop
  (backend) + frontend en Cloudflare Pages (gratis). Ver sección "Coste".
- **Región Fly**: París (`cdg`) — definida en los `fly.toml`.
- **HTTPS**: automático tanto en Fly como en Cloudflare, sin configuración extra.
- **Dominio custom**: en Cloudflare Pages (frontend) o `fly certs add` (si algún
  servicio sigue en Fly con dominio propio).
