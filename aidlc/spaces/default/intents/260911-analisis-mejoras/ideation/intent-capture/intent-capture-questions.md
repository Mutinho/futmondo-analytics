# Intent Capture — Preguntas de Enmarcado

## Sources

- [desc] Initial description: "Analizar el proyecto completo futmondo-analytics (arquitectura, codigo, infraestructura) e identificar mejoras y puntos criticos-debiles para abordarlos en futuros intents; generar un plan"
- [scope] Workflow-selected scope: `analysis-plan`.

## Q1. ¿Cuál es el problema o la motivación real detrás de este análisis?

Es decir, ¿qué te ha llevado a querer auditar el proyecto ahora? Esto orienta qué ejes priorizamos en el plan.

- A. Preparar el proyecto para crecer / añadir funcionalidades con más seguridad (deuda técnica antes de escalar).
- B. Preocupación concreta por fiabilidad o bugs recurrentes en producción.
- C. Preocupación por seguridad (auth, datos de usuarios, credenciales de Futmondo).
- D. Rendimiento / coste (sincronizaciones lentas, llamadas a APIs externas, factura de Fly.io/Neon).
- E. Ninguna urgencia concreta; quiero una foto general de salud del proyecto y un backlog de mejoras.
- X. Other (please specify)

[Answer]: A. Preparar el proyecto para crecer / reducir deuda técnica antes de escalar (manteniendo barrido general amplio como lente de priorización)

## Q2. ¿Quién usa el sistema y quién es el "cliente" de este análisis?

El proyecto es una PWA multi-usuario de fantasy football. ¿Para quién es el resultado del análisis?

- A. Uso personal / grupo reducido de amigos; el análisis es para mí como único desarrollador-mantenedor.
- B. Base de usuarios en crecimiento; me preocupa la experiencia de esos usuarios.
- C. Es un proyecto de aprendizaje/portfolio; el análisis es para mejorar mis prácticas.
- D. No identificado todavía.
- X. Other (please specify)

[Answer]: A. Uso personal / grupo reducido de amigos; único desarrollador-mantenedor

## Q3. ¿Cómo será un buen resultado de este trabajo? ¿Qué métricas o señales importan?

- A. Una lista priorizada de mejoras/puntos débiles accionable (backlog para futuros intents).
- B. Además, un mapa claro de la arquitectura actual (documentación que hoy no existe o está incompleta).
- C. Además, criterios objetivos de calidad (cobertura de tests, checklist de seguridad, objetivos de rendimiento).
- D. Todo lo anterior.
- X. Other (please specify)

[Answer]: D. Todo lo anterior (backlog priorizado + mapa de arquitectura + criterios objetivos de calidad)

## Q4. ¿Hay áreas del proyecto que YA sabes que son débiles o que quieres que miremos con lupa?

Cualquier sospecha previa nos ayuda a no pasarla por alto. (Selecciona todas las que apliquen.)

- A. Autenticación / gestión de sesiones y tokens (JWT, cookies, sesión Futmondo).
- B. Integraciones externas (API Futmondo, API Sofascore vía curl_cffi) y su fragilidad/rate-limits.
- C. La sincronización async de 11 pasos (fiabilidad, reintentos, estado de tareas).
- D. Tests / CI (frontend sin specs visibles, cobertura backend).
- E. Ninguna en particular / no lo sé, quiero que el análisis lo descubra.
- X. Other (please specify)

[Answer]: B, C, D. Integraciones externas (Futmondo/Sofascore); sincronización async de 11 pasos; tests/CI. (auth se analiza igualmente por ser sensible; barrido general se mantiene)

## Q5. ¿Hay restricciones o límites que el plan deba respetar?

Por ejemplo, tecnologías que NO quieres cambiar, presupuesto, o que el sistema debe seguir funcionando sin interrupciones.

- A. Mantener el stack actual (Angular + FastAPI + Neon + Fly.io); las mejoras no deben proponer reescrituras grandes.
- B. Restricción de coste (mantener infra barata/serverless).
- C. Sin restricciones fuertes; abiertos a proponer cambios de fondo si se justifican.
- D. No identificado todavía.
- X. Other (please specify)

[Answer]: A, B. Mantener el stack actual (sin reescrituras grandes) + restricción de coste. RESTRICCIÓN DURA: el proyecto debe mantenerse SIEMPRE a coste 0€ — el plan solo puede proponer mejoras sostenibles en tiers gratuitos (Neon free, Fly.io free allowance, GitHub Actions free) y debe descartar cualquier recomendación con gasto recurrente.

## Q6. ¿Quién decide qué mejoras se abordan y en qué orden?

- A. Yo mismo, soy quien prioriza y ejecuta.
- B. Yo decido pero quiero recomendaciones de prioridad claras (crítico / importante / opcional).
- C. Not applicable.
- X. Other (please specify)

[Answer]: B. Yo decido, con recomendaciones de prioridad claras (crítico / importante / opcional) y su justificación

## Q7. El workflow arrancó con el alcance `analysis-plan` (analizar y producir un plan, sin escribir código ni desplegar). ¿Coincide con el límite de producto que tienes en mente?

- A. Sí, exactamente: solo análisis + plan; la implementación irá en futuros intents.
- B. Mayormente, pero además quiero que el plan incluya un diseño preliminar de infraestructura/NFR (no solo enumerarlos).
- C. No: en realidad quiero empezar a implementar alguna mejora ya en este mismo trabajo.
- X. Other (please specify)

[Answer]: A. Sí, exactamente: solo análisis + plan; la implementación irá en futuros intents

## Consolidated Summary Confirmation

- Looks correct
- Request changes

[Answer]: Looks correct

## Assumption Confirmation

Asunciones detectadas en los artefactos:

- [assumption] No se ha definido una cadencia formal de reporte; al ser un mantenedor único, se asume que no es necesaria más allá de la entrega del plan.

Opciones:
- A. Accept assumptions
- B. Convert to follow-up questions

[Answer]: A. Accept assumptions
