**Collaborator:** aidlc-developer-agent

## Contribution

Revisión independiente (spoke ciego) del borrador del lead desde la óptica de
desarrollo: naming, límites de capas, manejo de errores, organización de
ficheros y convenciones de code-style, con foco en el área de premios. Baso los
hallazgos en `codekb/futmondo-analytics/{code-structure.md,architecture.md}`,
`backend/ruff.toml` y `angular-app/eslint.config.js`.

### 1. Límites de capas al tocar premios (lo esencial de este intent)

La evidencia deja el mapa de capas nítido y hay que respetarlo al modificar el
cálculo de premios:

- **Regla de oro: la fórmula NO baja de capa ni sube de capa.** Hoy
  `data_sync_service.sync_prizes()` mezcla en un mismo método tres
  responsabilidades distintas: (a) **ingesta** desde la API Futmondo (I/O de red
  con `time.sleep()`), (b) **cálculo puro** de los términos del premio
  (`points_prize`, `ranking_prize`, `mvp_prize`, `dream_team_prize` + el gating
  `is_closed AND round_fully_played AND NOT pseudo_ronda`), y (c) **persistencia**
  (UPSERT `ON CONFLICT` + limpieza `DELETE ... NOT IN` sobre `team_prizes`). El
  refactor correcto extrae **el cálculo puro** a una función/módulo sin I/O ni
  SQL — determinista, testeable con entradas en memoria — y deja ingesta y
  persistencia como colaboradores inyectados. Esa separación es lo que hace
  posible la caracterización a coste 0 € (dobles de la API + almacén en memoria)
  que el lead describe bien.

- **Dirección de dependencias (respetar el desacople existente).** La
  arquitectura ya separa una **mitad de escritura** (`sync_prizes` → `team_prizes`)
  de una **mitad de lectura** (routers `balances.py`/`player_finances.py` →
  `SELECT`/suma). Ese desacople por la tabla `team_prizes` es un buen límite: el
  nuevo código de cálculo debe seguir alimentando `team_prizes` como fuente de
  verdad y **NO** introducir recálculo en la ruta de lectura de los routers. Los
  endpoints siguen siendo lectores baratos.

- **Persistencia tras capa estrecha, nunca SQL nuevo en router.** Ya existe
  `backend/app/stores/` (capa estrecha del intent previo de durabilidad) y
  `models/` no tiene modelo de premios. Cualquier acceso nuevo a `team_prizes`
  para el cálculo debe ir por una función repositorio (patrón `stores/`), **sin**
  ampliar el SQL crudo disperso en `balances.py`/`analytics.py`/`_helpers.py`. La
  regla `NEVER ampliar el patrón SQL-en-router` del borrador es correcta; añado
  que la mitad de lectura ya existente **puede quedarse como está** (no es
  objetivo de este intent reescribir los `SELECT` existentes), pero **no debe
  crecer**.

- **El god-file no engorda: se adelgaza o queda igual.** `data_sync_service.py`
  (~84 KB) y `data_manager_v2.py` (~166 KB) no deben ganar líneas netas por este
  intent. Extraer la fórmula a un módulo nuevo estrecho (p. ej.
  `services/prizes/` o un `prize_calculator.py` sin I/O) es la forma de tocar
  premios *reduciendo* la superficie del god-file, no ampliándola. `sync_prizes`
  pasa a **orquestar** (ingesta → llamar al cálculo puro → persistir) en vez de
  contener todo.

### 2. Naming (refuerzo, con foco en la doble semántica de "puntos")

- **La doble semántica de "puntos" es un riesgo de naming real y debería
  nombrarse explícitamente en el código nuevo.** Hoy conviven `round_points`
  (métrica deportiva) y `points_prize` (importe monetario derivado
  `round(round_points * money_per_point)`). Al extraer la fórmula, el naming debe
  desambiguar sin lugar a dudas: reservar `*_points` para la métrica y `*_prize`
  / `*_amount` (o sufijo monetario) para el dinero. Esto es prevención de bugs,
  no cosmética: mezclar ambas semánticas en una variable es exactamente la clase
  de error que la caracterización busca congelar.

- **Consistencia con lo existente.** snake_case en Python, camelCase en TS
  (confirmado en `code-structure.md`); identificadores/docstrings/comentarios en
  **inglés**, texto de usuario (`HTTPException.detail`) en **castellano**. El
  borrador ya lo recoge en Code Style; correcto.

### 3. Manejo de errores en la mitad de escritura (matiz que el borrador no
detalla)

- El cálculo depende de la API Futmondo (`time.sleep()` entre llamadas) y de
  datos de ronda que pueden llegar incompletos (ronda no cerrada, no jugada del
  todo, pseudo-jornada negativa). El gating actual
  (`award_round_prizes = is_closed AND round_fully_played AND NOT pseudo_ronda`)
  **es** el manejo de error de dominio: hay que caracterizarlo tal cual antes de
  tocarlo. Recomiendo que la fórmula extraída **falle explícito o devuelva un
  resultado tipado "no premiable"** ante datos incompletos, en vez de calcular
  importes silenciosamente sobre rondas a medias. Alineado con el guardrail de
  fase de Construction ("errores en fronteras de integración; nada de fallos
  silenciosos"); el límite API↔cálculo es una de esas fronteras.

- La limpieza defensiva `DELETE ... WHERE matchday NOT IN (...)` es
  destructiva-en-batch: debe permanecer en la capa de **persistencia**, con su
  conjunto `valid_matchdays` calculado aguas arriba y caracterizado (qué borra y
  qué preserva), nunca embebida dentro de la lógica de cálculo puro.

### 4. Organización de ficheros

- El módulo de cálculo extraído y sus tests deben vivir agrupados por feature
  (patrón recomendado en el KB de code-generation): p. ej. `services/prizes/` con
  el cálculo puro + su test de caracterización adyacente, en vez de más líneas en
  `data_sync_service.py`. El repo ya expone `stores/` como precedente de capa
  estrecha nueva; seguir ese mismo criterio de ubicación.

### 5. Convenciones de code-style / linter (consistencia con la config real)

- `backend/ruff.toml` confirma `select = ["E","F","I"]`, `ignore =
  ["E501","E402","E722"]`, `line-length = 100`, `format` comillas dobles, y
  `per-file-ignores` para `tests/**` y `conftest.py`. **El código nuevo debe
  nacer ya conforme a ruff** (imports ordenados por `I`, sin F-flags), de modo
  que cuando `ruff check` pase a bloqueante no arrastre deuda — y sin necesidad de
  `ruff format` masivo. La regla `NEVER ruff format masivo brownfield` del
  borrador es correcta y crítica para no invalidar el pase de revisión en vuelo;
  el módulo nuevo, al estar aislado, sí puede formatearse quirúrgicamente.
- `angular-app/eslint.config.js` es flat config **advisory** (reglas base a
  `warn`, selectores `app`); este intent es backend-céntrico (premios en batch),
  así que el frontend no debería recibir cambios salvo lectura. Correcto no
  matizar frontend en el borrador.
- **Imports estáticos**: `code-structure.md` documenta imports dinámicos dentro
  de funciones como anti-patrón que el equipo está migrando (`refresh` ya migró).
  El código nuevo de premios debe usar import estático a nivel de módulo. El
  borrador ya lo recoge.

### 6. Incertidumbres para la interview (desde desarrollo)

Refuerzo, sin duplicar, las incertidumbres del lead que tienen carga técnica de
implementación:

- **Alcance del refactor (incertidumbre 1)**: desde desarrollo, extraer el
  **cálculo puro** a un módulo estrecho es lo que habilita la caracterización
  barata y respeta los límites de capa; corregir *in situ* sin extracción deja la
  fórmula enterrada en el god-file y dificulta el test. Recomiendo la extracción,
  pero es decisión de alcance del humano.
- **Doble semántica de "puntos" e identidad frágil en `player_finances`
  (incertidumbre 6)**: la resolución de identidad por nombre en `player_finances`
  es deuda real (frágil ante homónimos/renombrados). Recomiendo **documentarla
  como deuda fuera de alcance** salvo que toque directamente el importe del
  premio calculado en este intent; ampliar el alcance a arreglar identidad
  arriesga el "sin reescrituras grandes". Decisión del humano.

## Positions

- AGREE: `NEVER ampliar los god-files ni el patrón SQL-en-router; el código nuevo tras capa/función estrecha testeable` — coincide exactamente con el mapa de capas de la evidencia; es el límite que hace viable el refactor de premios.
- AGREE: `Testing Posture` test-after + characterization-first de `sync_prizes` (producción del premio, hoy cobertura cero) — el desacople escritura/lectura por `team_prizes` permite caracterizar la mitad de escritura con dobles a coste 0 €; el orden de dos fases es el correcto.
- AGREE: `NEVER ruff format masivo sobre brownfield modificado; formatear solo lo nuevo o quirúrgicamente` — consistente con `ruff.toml` (hoy advisory) y protege el pase de revisión; el módulo nuevo aislado sí puede formatearse.
- AGREE: Code Style — idioma inglés en identificadores/docstrings/comentarios, castellano en texto de usuario y commits; imports estáticos — coincide con lo observado en `code-structure.md`.
- OBJECT: `Code Style` no explicita que la extracción de la fórmula debe separar **cálculo puro (sin I/O ni SQL)** de ingesta y persistencia — sin esa separación de tres responsabilidades, "capa estrecha testeable" queda ambiguo y la caracterización a coste 0 € no es realizable; propongo que Code Style o discovered-rules lo declare explícito.
- OBJECT: falta una nota sobre **naming desambiguador de la doble semántica de "puntos"** (`*_points` métrica vs `*_prize`/`*_amount` dinero) en el código nuevo — es prevención directa de la clase de bug que se está caracterizando; debería quedar en Code Style aunque la deuda existente en `player_finances` se difiera.
