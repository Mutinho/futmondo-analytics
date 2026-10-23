# SLO Config — Sistema de diseño nativo iOS

> Fase: operación. Idioma: castellano; tokens técnicos verbatim en inglés.

NO-APLICA: no hay SLO de servicio para una capa de diseño cliente (sin disponibilidad/latencia de servidor que medir). Los SLO formales con burn-rate exigen tooling gestionado (de pago) ausente en el stack; coste 0 € lo descarta. El "objetivo" de la capa de diseño es cualitativo (render fluido 60 fps, fidelidad del tema), validado en dispositivo, no un SLO con ventana temporal.

Backend/frontend producción: su verificación de release sigue siendo el smoke `/health` heredado (`fly-deploy.yml`), no un SLO formal, y no cambia.

## Assumptions & Open Questions

None.
