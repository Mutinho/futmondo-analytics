# Preguntas de Análisis de Requisitos — FR13 Descomposición de god files

> Intent `260927-god-files-refactor`. Deriva del análisis `260911-analisis-mejoras` (FR13) y del backlog `docs/BACKLOG-plan-intents.md` (Intent 3). Scope `refactor`, brownfield, depth Minimal. Conversation language: Spanish.
>
> El escaneo (reverse-engineering) ya caracterizó los cuatro god files, sus seams de extracción, la superficie pública a preservar y la cobertura de tests actual (ver `codekb/futmondo-analytics/code-structure.md` y `code-quality-assessment.md`). Estas preguntas fijan **alcance y secuenciación** antes de redactar los requisitos. Todo lo demás (characterization-first, no ampliar god files, no reformatear en masa, no relajar cobertura, coste 0 €) ya está afirmado como regla del proyecto y NO se re-pregunta.

## Q1 — Alcance de este intent: ¿cuántos god files entran?

El análisis marcó FR13 como esfuerzo L multi-Bolt y recomendó "planificar aparte". Los cuatro difieren mucho en riesgo: `analytics_service.py` está bien cubierto (menor riesgo), mientras `data_manager_v2.py` (3692 líneas, cobertura ~cero) es el núcleo del acoplamiento y el más peligroso.

- A. **Solo `analytics_service.py`** — la primera oleada de menor riesgo; probar el patrón de extracción end-to-end antes de comprometerse con más.
- B. **`analytics_service.py` + `assistant_service.py`** — los dos "hoja" (no son el núcleo de acoplamiento); `data_manager_v2.py` y `data_sync_service.py` se dejan a un intent posterior.
- C. **Los cuatro, pero por oleadas gated** — plan incremental completo en este intent, cada god file (o dominio) en su propio Bolt con aprobación, empezando por el de menor riesgo.
- D. **Solo `data_manager_v2.py`** — atacar primero el núcleo del acoplamiento porque desbloquea la extracción limpia de sync y analytics.
- X. Other (please specify)

[Answer]: C. Los cuatro, pero por oleadas gated. (Recomendación del conductor, aceptada por el usuario: "Dame tus recomendaciones".) El análisis marcó FR13 como esfuerzo L multi-Bolt; abordarlo completo pero con cada god file/dominio en su propio Bolt aprobado mantiene la red de seguridad y permite parar entre oleadas.

## Q2 — Orden de ataque

Si entran varios (Q1=B/C), ¿qué orden de riesgo/valor prefieres?

- A. **Menor riesgo primero**: `analytics_service` → `assistant_service` → `data_sync_service` → `data_manager_v2` (valida el patrón donde hay red de tests, deja el núcleo peligroso para el final con la red ya reforzada).
- B. **Núcleo primero**: `data_manager_v2` → resto (una vez extraído el DM en repositorios, sync y analytics se apoyan en interfaces estrechas).
- C. **Por valor de desacoplamiento**: `data_sync_service` primero (sus `sync_*` ya son unidades naturales y hay caracterización de efecto parcial), luego el resto.
- X. Other (please specify)

[Answer]: A. Menor riesgo primero: `analytics_service` → `assistant_service` → `data_sync_service` → `data_manager_v2`. (Recomendación aceptada.) Valida el patrón de extracción donde ya hay red de tests (analytics tiene el seam de inyección probado) y deja el núcleo de acoplamiento (`data_manager_v2`, cobertura ~cero) para el final, con la red de caracterización ya reforzada por las oleadas previas.

## Q3 — Profundidad de la extracción por god file (criterio de "hecho")

¿Hasta dónde llega la descomposición de cada fichero en su Bolt?

- A. **Fachada delgada + repositorios/módulos por dominio**: sacar la lógica a módulos por agregado/dominio detrás de la fachada pública existente (patrón `prizes/` + writer transaccional). Objetivo: reducir el fichero a un orquestador delgado.
- B. **Solo aislar la capa de datos (SqlGateway/repositorios)**: envolver los `cursor.execute` en repositorios, sin trocear la lógica de negocio por dominio todavía.
- C. **Extracción parcial pragmática por Bolt**: en cada Bolt extraer 1-2 dominios/seams bien cubiertos, sin exigir que el fichero quede "delgado" al final del intent.
- X. Other (please specify)

[Answer]: A. Fachada delgada + repositorios/módulos por dominio, replicando el patrón de referencia `prizes/` + writer transaccional. (Recomendación aceptada.) La superficie pública de cada god file se preserva como fachada que delega; la lógica se mueve a módulos por agregado/dominio detrás de ella, reduciendo el fichero a orquestador delgado sin cambiar comportamiento observable.

## Q4 — Umbral de reducción como criterio de aceptación

¿Fijamos un criterio de aceptación medible de reducción de tamaño, o el criterio es cualitativo (comportamiento preservado + seams extraídos)?

- A. **Cualitativo**: el criterio es "comportamiento preservado (tests de caracterización verdes) + al menos N dominios extraídos a módulos estrechos por god file tocado"; sin umbral numérico de líneas.
- B. **Con umbral orientativo**: además de lo cualitativo, fijar una meta orientativa (p. ej. reducir el god file tocado ≥30 % de líneas) como señal, no como gate duro.
- C. **Con gate duro de tamaño**: ningún fichero de servicio supera X líneas al cerrar su Bolt (arriesgado en brownfield; puede forzar troceo artificial).
- X. Other (please specify)

[Answer]: A. Cualitativo: el criterio de aceptación es "comportamiento preservado (tests de caracterización verdes + suite existente verde) + al menos N dominios/seams extraídos a módulos estrechos por god file tocado en su Bolt"; sin umbral numérico de líneas. (Recomendación aceptada.) En brownfield un gate duro de tamaño fuerza troceo artificial; la señal real es la extracción de seams con comportamiento congelado, no el conteo de líneas.

## Q5 — Red de caracterización previa (dónde invertir tests antes de mover código)

`data_manager_v2.py` y `assistant_service.py` tienen cobertura directa ~cero/cero. La regla afirmada exige characterization-first. ¿Cómo dimensionamos esa red antes de extraer?

- A. **Caracterizar solo los seams que se van a mover en cada Bolt** (just-enough): congelar el comportamiento observable de los métodos/dominios de ESE Bolt antes de tocarlos, no el fichero entero de golpe.
- B. **Caracterización amplia por fichero antes de empezar su descomposición**: congelar toda la superficie pública del god file antes del primer movimiento (más caro, más seguro).
- C. **Mixto**: superficie pública amplia para el fichero núcleo (`data_manager_v2`) y just-enough por seam para el resto.
- X. Other (please specify)

[Answer]: C. Mixto: superficie pública amplia para el fichero núcleo (`data_manager_v2`, cobertura ~cero y consumido por 8 routers + sync + analytics) antes de su descomposición, y just-enough por seam (congelar solo lo que se mueve en cada Bolt) para los otros tres. (Recomendación aceptada.) Concentra la inversión de caracterización donde el riesgo de regresión es máximo sin encarecer los ficheros de menor riesgo o mejor cubiertos.

## Consolidated Summary Confirmation

- **Alcance (Q1)**: los cuatro god files entran en este intent, pero por **oleadas gated** (cada god file/dominio en su propio Bolt aprobado).
- **Orden (Q2)**: menor riesgo primero — `analytics_service` → `assistant_service` → `data_sync_service` → `data_manager_v2`.
- **Profundidad / "hecho" (Q3)**: fachada pública delgada + repositorios/módulos por dominio, replicando el patrón `prizes/` + writer transaccional atómico; el god file queda como orquestador delgado.
- **Criterio de aceptación (Q4)**: cualitativo — comportamiento preservado (caracterización + suite existente verdes) + N dominios/seams extraídos por fichero tocado; sin umbral numérico de líneas.
- **Red de caracterización (Q5)**: mixta — amplia (superficie pública) para el núcleo `data_manager_v2` antes de tocarlo; just-enough por seam para los otros tres.
- **Reglas ya afirmadas (no re-preguntadas)**: characterization-first; NO ampliar god files ni el patrón SQL-en-router; NO `ruff format`/Prettier masivo; NO relajar umbrales de cobertura; preservar la superficie pública (`DataManagerV2.*`, `DataSyncService.sync_*`/`sync_all`, `get_assistant_service()`/`ask()`, `AnalyticsService.get_*`); coste 0 €; gate de CI bloqueante antes de merge a `main`.

Does this all look correct before I generate the requirements artifact?

[Answer]: Looks correct

