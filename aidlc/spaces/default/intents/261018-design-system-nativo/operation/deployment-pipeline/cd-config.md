# CD Config — Sistema de diseño nativo iOS

> Fase: operación. Idioma: castellano; tokens técnicos verbatim en inglés.

## Estado del CD del repositorio (heredado, no modificado)

- `.github/workflows/fly-deploy.yml`: `verify → deploy-backend → deploy-frontend → smoke-test` (`/health`, 5 reintentos). **Este intent NO lo toca.**
- La app iOS no está en ningún pipeline CD (se instala con `xtool` en dispositivo); añadir distribución automatizada (TestFlight/App Store) es trabajo futuro con la excepción de coste acotada (Apple Developer Program), no de este intent.

## Entrega iOS (manual, coste 0 €)

```
cd ios && swift build && swift test   # verificación
cd ios && xtool dev build             # construir/instalar en iPhone 13 Pro (firma gratuita)
```

## Assumptions & Open Questions

None.
