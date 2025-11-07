# 🌐 Guía Rápida: Exponer Futmondo API con ngrok

## 📋 Opción 1: Usar el Script (Más Simple)

### Paso 1: Instalar ngrok

```bash
# Con Homebrew (macOS)
brew install ngrok

# O descarga desde: https://ngrok.com/download
```

### Paso 2: Configurar tu authtoken (solo la primera vez)

1. Regístrate en [ngrok.com](https://dashboard.ngrok.com/signup) (gratis)
2. Copia tu authtoken desde el [dashboard](https://dashboard.ngrok.com/get-started/your-authtoken)
3. Configúralo:

```bash
ngrok config add-authtoken TU_AUTHTOKEN_AQUI
```

### Paso 3: Iniciar el backend y frontend

```bash
# Terminal 1: Backend
cd backend
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# Terminal 2: Frontend
./start-frontend.sh

# Terminal 3: ngrok (expone el frontend)
./start-ngrok.sh
```

### Paso 4: Obtener tu URL pública

Cuando ejecutes `./start-ngrok.sh`, verás algo como:

```
Forwarding  https://xxxx-xxxx-xxxx.ngrok-free.app -> http://localhost:3000
```

**¡Esa es tu URL pública!** Compártela para acceder a la aplicación.

---

## 📋 Opción 2: ngrok Automático en el Frontend

### Paso 1: Instalar dependencias

```bash
cd frontend
npm install @ngrok/ngrok
```

### Paso 2: Crear archivo `.env` en la raíz del proyecto

```bash
# En la raíz del proyecto (FutmondoAPI/)
cat > .env << EOF
NGROK_ENABLED=true
NGROK_AUTHTOKEN=tu_authtoken_aqui
API_URL=http://localhost:8000
PORT=3000
EOF
```

### Paso 3: Iniciar servicios

```bash
# Terminal 1: Backend
cd backend
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# Terminal 2: Frontend (ngrok se iniciará automáticamente)
cd frontend
npm start
```

Verás en los logs:

```
🌐 ============================================
🌐 ngrok tunnel established!
🌐 Public URL: https://xxxx-xxxx-xxxx.ngrok-free.app
🌐 ============================================
```

---

## 🔍 Verificar que Funciona

1. Abre la URL de ngrok en tu navegador
2. Deberías ver la aplicación funcionando
3. Las llamadas a `/api/*` se redirigen automáticamente al backend

---

## ⚠️ Notas Importantes

### URLs Temporales
- En el plan gratuito, la URL cambia cada vez que reinicias ngrok
- Para URLs estables, necesitas un plan de pago

### Seguridad
- La aplicación será accesible públicamente
- Solo comparte la URL con personas de confianza
- No expongas información sensible sin protección adicional

### Límites del Plan Gratuito
- Puede mostrar una página de advertencia en la primera visita
- Límites en conexiones simultáneas
- URLs que cambian al reiniciar

---

## 🐛 Troubleshooting

### Error: "ngrok no está instalado"
```bash
brew install ngrok  # macOS
# O descarga desde https://ngrok.com/download
```

### Error: "Frontend no está corriendo"
```bash
./start-frontend.sh
```

### Error: "NGROK_AUTHTOKEN is not set"
1. Obtén tu authtoken desde https://dashboard.ngrok.com/get-started/your-authtoken
2. Configúralo: `ngrok config add-authtoken TU_TOKEN`

### La URL no funciona
1. Verifica que el frontend está corriendo: `curl http://localhost:3000`
2. Verifica que el backend está corriendo: `curl http://localhost:8000/api/v1/matchdays/evolution`
3. Revisa los logs de ngrok

---

## 💡 Tips

- **URLs reservadas**: Con plan de pago puedes tener URLs que no cambian
- **Dominios personalizados**: Los planes de pago permiten usar tu propio dominio
- **Webhooks**: ngrok es excelente para probar webhooks durante desarrollo

---

## 📚 Recursos

- [Documentación ngrok](https://ngrok.com/docs)
- [Dashboard ngrok](https://dashboard.ngrok.com)
- [Precios ngrok](https://ngrok.com/pricing)

