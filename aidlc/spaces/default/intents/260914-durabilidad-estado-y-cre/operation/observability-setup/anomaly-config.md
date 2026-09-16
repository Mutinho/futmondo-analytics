# Anomaly Detection Config — Durabilidad del estado (NO-APLICA a coste 0 €)

> Etapa Observability Setup (Operation). La detección de anomalías con ML (CloudWatch Anomaly
> Detection, bandas basadas en desviación estándar) requiere un sistema de métricas de pago. Bajo el
> mandato de coste 0 €, NO se configura detección de anomalías automatizada en este intent.

## Estado: NO-APLICA a coste 0 €

- **Motivo**: requiere métricas continuas y ML gestionado de pago; incompatible con coste 0 €.

## Alternativa gratuita (actual)

- **Revisión manual de picos por logs**: las señales de durabilidad tienen patrones esperados
  (p. ej. un pico de `interrupted_by_restart` correlaciona 1:1 con un redeploy). Una desviación de ese
  patrón (p. ej. tareas interrumpidas sin redeploy, o 401 sostenidos con el secret presente) se detecta
  por revisión de `fly logs` (ver `log-queries.md`), no por ML.
- **Healthcheck**: una anomalía aguda (servicio no responde) la captura el check de Fly.io y el smoke
  test, sin ML.

## Recomendación

- Diferido a un eventual tier de pago. Para un proyecto personal de bajo volumen, la revisión manual
  de logs ante eventos conocidos (redeploy, rotación de secret, reporte de usuario) es suficiente y de
  coste 0 €.
