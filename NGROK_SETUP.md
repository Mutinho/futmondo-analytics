# 🌐 Configuración de ngrok - Futmondo API

Esta guía explica cómo configurar ngrok para exponer el frontend públicamente.

## 📋 ¿Qué es ngrok?

[ngrok](https://ngrok.com) es un servicio que crea túneles seguros desde internet hasta tu aplicación local, permitiendo que otros usuarios accedan a tu frontend desde cualquier lugar del mundo.

## 🚀 Configuración Rápida

### 1. Obtener tu Authtoken de ngrok

1. **Regístrate** en [ngrok](https://dashboard.ngrok.com/signup) (es gratis)
2. **Inicia sesión** en el [Dashboard de ngrok](https://dashboard.ngrok.com/get-started/your-authtoken)
3. **Copia tu authtoken** - Lo encontrarás en la sección "Your Authtoken"

### 2. Configurar Variables de Entorno

Edita tu archivo `.env` y agrega:

```env
NGROK_ENABLED=true
NGROK_AUTHTOKEN=tu_authtoken_aqui
```

### 3. Reiniciar los Servicios

Si usas Docker:

```bash
docker-compose restart frontend
```

O reinicia todos los servicios:

```bash
docker-compose down
docker-compose up -d
```

Si no usas Docker, reinicia el servidor frontend manualmente.

## ✅ Verificación

Una vez configurado, verás en los logs del frontend:

```
🌐 ============================================
🌐 ngrok tunnel established!
🌐 Public URL: https://xxxx-xxxx-xxxx.ngrok-free.app
🌐 ============================================
```

**¡Esa es tu URL pública!** Compártela con tus amigos para que puedan acceder al frontend.

## 🔍 Ver Logs

Para ver los logs y confirmar que ngrok está funcionando:

```bash
# Con Docker
./docker-logs.sh frontend

# O directamente
docker-compose logs -f frontend
```

## ⚙️ Configuración Avanzada

### Variables de Entorno

En tu archivo `.env`:

- `NGROK_ENABLED=true` - Habilita ngrok
- `NGROK_AUTHTOKEN=tu_token` - Tu authtoken de ngrok

### Deshabilitar ngrok

Para deshabilitar ngrok, simplemente establece:

```env
NGROK_ENABLED=false
```

O elimina la variable `NGROK_ENABLED` del archivo `.env`.

## 🌍 Limitaciones del Plan Gratuito

El plan gratuito de ngrok tiene algunas limitaciones:

- **URLs temporales**: La URL cambia cada vez que reinicias el túnel (a menos que uses un dominio reservado)
- **Límites de conexión**: Puede haber límites en el número de conexiones simultáneas
- **Página de advertencia**: Puede mostrar una página de advertencia en la primera visita

### Planes de Pago

Si necesitas URLs estables, dominios personalizados o más características, puedes actualizar a un plan de pago en [ngrok pricing](https://ngrok.com/pricing).

## 🔐 Seguridad

⚠️ **Importante**: Cuando expones tu aplicación con ngrok, está accesible públicamente en internet.

- Solo comparte la URL con personas de confianza
- No expongas información sensible sin protección adicional
- Considera implementar autenticación si es necesario

## 🐛 Troubleshooting

### Error: "NGROK_AUTHTOKEN is not set"

Asegúrate de que:
1. Has agregado `NGROK_AUTHTOKEN` en tu archivo `.env`
2. Has reiniciado el servicio después de agregar la variable
3. El token es válido

### Error: "Error establishing ngrok tunnel"

1. Verifica que tu authtoken es correcto
2. Asegúrate de que tienes conexión a internet
3. Verifica los logs con `./docker-logs.sh frontend`

### La URL no funciona

1. Verifica que el frontend está corriendo: `./docker-status.sh`
2. Verifica los logs: `./docker-logs.sh frontend`
3. Asegúrate de que `NGROK_ENABLED=true` en tu `.env`

## 📚 Recursos

- [Documentación oficial de ngrok](https://ngrok.com/docs)
- [ngrok Node.js SDK](https://ngrok.com/download/node-js)
- [Dashboard de ngrok](https://dashboard.ngrok.com)

## 💡 Tips

- **URLs reservadas**: Si tienes un plan de pago, puedes reservar una URL para que no cambie
- **Dominios personalizados**: Los planes de pago permiten usar tu propio dominio
- **Webhooks**: ngrok es excelente para probar webhooks durante el desarrollo

---

**¿Necesitas ayuda?** Consulta los logs con `./docker-logs.sh frontend` o revisa la [documentación de ngrok](https://ngrok.com/docs).








