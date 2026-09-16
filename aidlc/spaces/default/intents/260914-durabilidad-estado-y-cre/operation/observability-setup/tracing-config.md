# Tracing Config — Durabilidad del estado (NO-APLICA a coste 0 €)

> Etapa Observability Setup (Operation). El tracing distribuido (AWS X-Ray, OpenTelemetry con backend
> gestionado) requiere infraestructura de pago o un colector autogestionado. Bajo el mandato de coste
> 0 € y dado que el backend es un único servicio FastAPI (no un sistema distribuido de múltiples
> servicios), NO se configura tracing distribuido en este intent.

## Estado: NO-APLICA a coste 0 €

- **Motivo**: coste 0 €; arquitectura de un solo servicio backend (no hay múltiples saltos de servicio
  que trazar). El valor del tracing distribuido es marginal aquí.

## Alternativa gratuita (actual)

- **Correlación por logs**: para diagnosticar un flujo (p. ej. login → rehidratación → petición
  autenticada), usar `fly logs` con un identificador correlacionable. Si se adopta logging
  estructurado (recomendado en `log-queries.md`), incluir un `request_id` estable por petición permite
  seguir el flujo sin un sistema de tracing de pago.

## Recomendación

- Si en el futuro el backend se descompone en varios servicios, reconsiderar OpenTelemetry con un
  backend gratuito/self-hosted. Hoy no aporta a coste 0 €.
