# Scope Definition — Preguntas

## Sources

- [desc] Initial description: "Analizar el proyecto completo futmondo-analytics (arquitectura, codigo, infraestructura) e identificar mejoras y puntos criticos-debiles para abordarlos en futuros intents; generar un plan"
- [scope] Workflow-selected scope: `analysis-plan`.

## Q1. ¿Qué ejes de análisis entran en el alcance (in-scope) de esta auditoría?

Propuesta de ejes a cubrir. (Selecciona todos los que apliquen; puedes quitar alguno.)

- A. Arquitectura y estructura de código (frontend Angular, backend FastAPI, límites entre capas).
- B. Seguridad (auth/JWT/cookies, manejo de credenciales Futmondo, exposición de datos, secretos).
- C. Fiabilidad y robustez (sincronización async de 11 pasos, manejo de errores, integraciones externas Futmondo/Sofascore).
- D. Rendimiento y coste (latencia de sync, llamadas a APIs externas, consumo de recursos dentro de tiers gratuitos).
- E. Calidad y prácticas de ingeniería (tests, CI/CD, linters, tipado, documentación).
- X. Other (please specify)

[Answer]: A, B, C, D, E. Los cinco ejes: arquitectura/código, seguridad, fiabilidad/robustez, rendimiento/coste, calidad/prácticas de ingeniería

## Q2. ¿Qué queda explícitamente FUERA del alcance (out-of-scope) de este trabajo?

- A. Implementar cualquier mejora (todo cambio de código va a futuros intents); diseño detallado de cada mejora; despliegue.
- B. Además, quedan fuera cambios de la UI/UX (rediseño visual).
- C. Además, queda fuera cualquier análisis de aspectos legales/regulatorios (RGPD, etc.).
- D. Solo A.
- X. Other (please specify)

[Answer]: A. Fuera: implementar mejoras (van a futuros intents), diseño detallado de cada mejora, y despliegue. (UX y aspectos legales/datos SÍ pueden señalarse como puntos débiles en el backlog aunque no se rediseñen ni se dictaminen aquí)

## Q3. ¿Qué marco de priorización usamos para el backlog de mejoras?

Ya acordamos etiquetas crítico / importante / opcional. ¿Cómo definimos "crítico"?

- A. Crítico = riesgo real de rotura en producción o de seguridad/pérdida de datos; Importante = deuda técnica que frena el crecimiento o la mantenibilidad; Opcional = mejora deseable de bajo impacto.
- B. Priorizar por esfuerzo/retorno (quick wins primero) además de por gravedad.
- C. Ambas cosas: severidad como eje principal y esfuerzo/retorno como desempate.
- X. Other (please specify)

[Answer]: C. Severidad como eje principal (crítico = riesgo de rotura/seguridad/pérdida de datos; importante = deuda que frena crecimiento/mantenibilidad; opcional = mejora deseable de bajo impacto) + esfuerzo/retorno como desempate dentro de cada nivel

## Q4. ¿Cuál es el "mínimo entregable con valor" de este análisis?

Es decir, si solo diera tiempo a una cosa, ¿qué es imprescindible?

- A. El backlog priorizado de mejoras (aunque el mapa de arquitectura quede más ligero).
- B. El mapa de arquitectura actual (documentación), aunque el backlog sea más breve.
- C. Ambos son imprescindibles a partes iguales.
- X. Other (please specify)

[Answer]: A. El backlog priorizado de mejoras es el mínimo entregable con valor (el mapa de arquitectura es soporte y se produce igualmente)

## Consolidated Summary Confirmation

- Looks correct
- Request changes

[Answer]: Looks correct
