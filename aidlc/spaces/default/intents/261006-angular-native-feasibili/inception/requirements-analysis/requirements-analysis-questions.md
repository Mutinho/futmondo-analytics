# Requirements Analysis — Preguntas de clarificación

Intent de **análisis de viabilidad** de migración a Angular Native (NativeScript + Angular).
La descripción ya fija los cuatro ejes (menú inferior iOS, widgets iOS/Android, viabilidad/encaje
con el stack, ruta de implementación) y practices-discovery ya resolvió: coste Apple como excepción
acotada, riesgo de sesión nativa dentro del análisis, detalle del arnés de test diferido. Estas
preguntas afinan el **alcance y la profundidad del documento de viabilidad** (no de una
implementación).

## Q1 — Veredicto esperado del análisis

¿Qué forma de conclusión esperas del documento de viabilidad?

- A. **Recomendación binaria** (viable / no viable) con justificación y condiciones.
- B. **Recomendación con alternativas comparadas** (Angular Native vs. mantener/mejorar la PWA actual vs. otra vía nativa como Capacitor), con una recomendada.
- C. **Sólo mapa de riesgos y esfuerzo** sin recomendación final; la decisión la toma el humano después.
- D. Recomendación binaria + comparación ligera con la PWA actual como línea base.
- X. Other (please specify)

[Answer]:

## Q2 — Profundidad de la ruta de implementación (eje 4)

La "ruta de implementación" del eje 4, ¿a qué nivel de detalle?

- A. **Fases de alto nivel** (hitos, orden, dependencias) sin estimación temporal.
- B. Fases **con estimación relativa de esfuerzo** (p. ej. T-shirt sizing S/M/L por fase).
- C. **Desglose fino** por componente/pantalla migrable (lista de módulos y su orden), apto para alimentar units/delivery-planning después.
- D. Alto nivel + identificación explícita del "walking skeleton nativo" mínimo que probaría la vía.
- X. Other (please specify)

[Answer]:

## Q3 — Alcance del análisis de paridad funcional

El frontend actual tiene ~13 áreas (presupuesto, mercado, sync, finanzas, evolución, estadísticas,
clausulables, analytics, asistente IA, PWA, dark mode, etc.). Para la viabilidad, ¿cómo tratamos
la paridad funcional?

- A. **Inventario completo** área por área con nota de portabilidad (portable 1:1 / adaptación / reconstrucción) para cada una.
- B. **Muestreo representativo**: analizar a fondo 3-4 áreas que ejemplifiquen los patrones (una con Chart.js, una con Material/CDK pesado, una de servicio puro, el asistente) y extrapolar.
- C. Centrarse sólo en lo que la descripción destaca (menú inferior, widgets) y tratar el resto como "reemplazo de presentación" genérico.
- X. Other (please specify)

[Answer]:

## Q4 — Widgets (eje 2): profundidad del análisis

Para el soporte de widgets iOS/Android, ¿qué nivel?

- A. **Viabilidad técnica + enfoque recomendado** (qué API/plugin, qué datos mostraría, límites de NativeScript para widgets nativos).
- B. Viabilidad + **diseño conceptual** de 1-2 widgets concretos (p. ej. "saldo del equipo", "próxima jornada").
- C. Sólo señalar si es **posible/imposible/parcial** y los bloqueantes, sin diseño.
- X. Other (please specify)

[Answer]:

## Q5 — Criterio de éxito del propio análisis

¿Cuándo consideras que este documento de viabilidad está "completo y útil"?

- A. Cuando responde con evidencia a los 4 ejes y da una recomendación accionable con riesgos y coste.
- B. Lo de A **más** una ruta que delivery-planning/units pueda consumir directamente si se aprueba seguir.
- C. Lo de A **más** una decisión go/no-go con criterios objetivos (umbrales de esfuerzo/riesgo que la harían no-viable).
- X. Other (please specify)

[Answer]:
