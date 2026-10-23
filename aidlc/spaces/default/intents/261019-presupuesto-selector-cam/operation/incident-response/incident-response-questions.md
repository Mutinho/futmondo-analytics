# Incident Response — Questions (F2)

> Fase: operación. Idioma: castellano; tokens técnicos verbatim en inglés.

## Consolidated Summary Confirmation

Resumen de Incident Response: sin incidentes de servidor nuevos (F2 es app cliente). Runbooks de los modos de fallo reales: **R1** regresión visual/funcional → `git revert` + reinstalar (sesión F1 intacta); **R2** firma gratuita caducada (~7 días) → refirmar con `xtool`; **R3** error de datos → la app degrada con Reintentar sin corromper el activo (si hay incoherencia de "saldo", es la deuda de backend ya registrada). **Single-maintainer sin on-call**. El backend conserva su propio proceso de incidentes, sin cambios por F2.

¿Does this all look correct?

[Answer]: Looks correct
