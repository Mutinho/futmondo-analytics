# Resultados de Smoke Test

## Ejecución
- Ejecutado por el pipeline `fly-deploy.yml` tras el deploy (backend + frontend).
- Verificación: endpoint `/health`.

## Resultado
- **`/health`: OK.** El servicio responde saludable tras el despliegue.
- Deploy backend (`futmondo-api`) y frontend (`futmondo-app`): OK.

## Cobertura del smoke
- Verifica disponibilidad del servicio post-deploy (health check). No cubre
  regresión funcional; esa la cubre la suite de pytest en el gate `verify`
  (54 passed) que precede al deploy.

## Veredicto
- Despliegue verificado como exitoso. Sin necesidad de rollback.
