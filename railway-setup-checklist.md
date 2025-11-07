# ✅ Checklist de Configuración para Railway

Usa este checklist para asegurarte de que todo está configurado correctamente antes de desplegar.

## 📋 Pre-despliegue

- [ ] Repositorio GitHub creado y código subido
- [ ] Cuenta de Railway creada
- [ ] Tarjeta de crédito añadida (para plan Hobby)

## 🗄️ Servicio PostgreSQL

- [ ] Servicio PostgreSQL creado en Railway
- [ ] Variable `DATABASE_URL` copiada (Railway la genera automáticamente)
- [ ] Servicio PostgreSQL está corriendo y saludable

## 🔧 Servicio Backend

- [ ] Servicio Backend creado desde GitHub repo
- [ ] Root Directory configurado: `/backend` o `backend`
- [ ] Dockerfile detectado correctamente
- [ ] Variables de entorno configuradas:
  - [ ] `FUTMONDO_EMAIL`
  - [ ] `FUTMONDO_PASSWORD`
  - [ ] `CHAMPIONSHIP_ID`
  - [ ] `LEAGUE_ID`
  - [ ] `DATABASE_URL` (debe ser `${{Postgres.DATABASE_URL}}` o el nombre de tu servicio PostgreSQL)
  - [ ] `DATABASE_TYPE=postgresql`
  - [ ] `API_HOST=0.0.0.0`
  - [ ] `API_PORT=8000`
- [ ] Dominio público generado para el backend
- [ ] Health check funcionando: `https://tu-backend.railway.app/health`

## 🎨 Servicio Frontend

- [ ] Servicio Frontend creado desde GitHub repo
- [ ] Root Directory configurado: `/frontend` o `frontend`
- [ ] Dockerfile detectado correctamente
- [ ] Variables de entorno configuradas:
  - [ ] `PORT=3000`
  - [ ] `API_URL` = URL pública del backend (ej: `https://backend-production-xxxx.up.railway.app`)
  - [ ] `NGROK_ENABLED=false`
- [ ] Dominio público generado para el frontend
- [ ] Frontend accesible en el navegador

## 🔗 Conexiones entre Servicios

- [ ] Backend puede conectarse a PostgreSQL (verificar logs)
- [ ] Frontend puede conectarse al Backend (verificar en navegador)
- [ ] CORS configurado correctamente en el backend

## ✅ Verificación Final

- [ ] Backend responde en `/health`
- [ ] Backend responde en `/api/v1/matchdays/evolution`
- [ ] Frontend carga correctamente
- [ ] Los gráficos se muestran en el frontend
- [ ] Sincronización de datos funciona: `/api/v1/sync/status`
- [ ] Cron job configurado (si es necesario)

## 🐛 Troubleshooting

Si algo no funciona:

1. **Revisa los logs** en Railway Dashboard → Servicio → Deployments → Logs
2. **Verifica variables de entorno** en Settings → Variables
3. **Comprueba las conexiones** entre servicios
4. **Revisa la documentación** en `RAILWAY_DEPLOY.md`

## 📞 Soporte

- [Railway Documentation](https://docs.railway.app)
- [Railway Discord](https://discord.gg/railway)

