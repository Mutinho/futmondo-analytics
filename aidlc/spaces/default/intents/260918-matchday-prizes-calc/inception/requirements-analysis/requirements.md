# Requisitos — Mejora del cálculo de premios de jornada (matchday-prizes-calc)

## Sources

- `[desc]` Initial description: `aidlc engine workspace project-description` →
  "Mejora del cálculo de premios de las jornadas (matchday prizes) en
  futmondo-analytics. Proyecto brownfield: Angular + FastAPI + Neon PostgreSQL +
  Fly.io; mantener el stack, sin reescrituras grandes, coste 0€ (tiers gratuitos)."
- `[Q1..Q6]` Respuestas de la interview en
  `requirements-analysis-questions.md` (checkpoint de resumen confirmado por el
  usuario).
- Petición del usuario (autoritativa, fuera de bloque de documento): descripción
  del bug con el campeonato `592416daa3a2dd871a7a9956`, jornada 5.
- Reverse-engineering (brownfield): `business-overview.md`, `architecture.md`,
  `code-structure.md` — ubican la fórmula en
  `data_sync_service.py::sync_prizes` (~1577-1885), productora de la tabla
  `team_prizes`; los routers solo leen/suman.
- `team-practices.md` (prácticas afirmadas de este intent).

## Análisis de intención

El objetivo es **corregir cómo se reparte el premio de ranking por jornada
cuando hay equipos empatados a puntos**. Hoy, el sistema (`sync_prizes`) asigna
a cada equipo el premio correspondiente a su posición individual, tomada del
orden en que la API de Futmondo devuelve el ranking. Cuando dos o más equipos
empatan a puntos, esto es incorrecto: cada empatado recibe el premio de una
posición concreta (dependiente de un orden arbitrario), en lugar del reparto
equitativo que aplica Futmondo.

Comportamiento correcto (confirmado por el usuario): cuando N equipos empatan a
puntos, se **suman los premios de las N posiciones que ese grupo ocupa** y la
suma se **reparte a partes iguales** entre los N empatados.

Ejemplo real (campeonato `592416daa3a2dd871a7a9956`, jornada 5): dos equipos
empatan ocupando las posiciones 3ª (premio 1.285.714) y 4ª (premio 1.714.286).
Suma = 3.000.000 → cada empatado recibe 1.500.000. Con tres empatados se sumarían
las tres posiciones y se dividiría entre 3.

El valor de negocio es que los importes de premio reflejen fielmente las reglas
de Futmondo, corrigiendo un cálculo que hoy produce importes erróneos en jornadas
con empates.

## Requisitos funcionales

### FR1 — Reparto equitativo del premio de ranking ante empates

- **FR1.1** Al calcular el premio de ranking de una jornada, el sistema DEBE
  agrupar los equipos premiables por su número de **puntos de la jornada**
  (`points`). Dos o más equipos con el mismo valor de puntos forman un grupo de
  empate. (Q3)
- **FR1.2** Para cada grupo de empate de N equipos que ocupa N posiciones, el
  sistema DEBE calcular la **suma de los premios de esas N posiciones** (según la
  fórmula de ranking vigente: `money_per_ranking * ratio`, con el `ranking_mode`
  configurado: `flop` o `top`) y **repartir esa suma a partes iguales** entre los
  N equipos del grupo: `premio_por_equipo = suma_posiciones / N`. Las N posiciones
  sumadas son las **contiguas** que el grupo ocupa una vez ordenados los equipos
  premiables por puntos de jornada (posiciones `p, p+1, …, p+N-1`), de modo que el
  resultado no dependa del orden arbitrario en que la API liste a los empatados.
  (petición del usuario; R-01 del review)
- **FR1.3** Un grupo de un solo equipo (sin empate) DEBE recibir exactamente el
  premio de su posición, idéntico al comportamiento actual (no hay regresión en
  el caso sin empates).
- **FR1.4** Cada premio individual resultante DEBE redondearse con `round()`
  (redondeo a entero más cercano), igual que el cálculo actual de importes. El
  reparto exacto del resto cuando `suma_posiciones / N` no es entero queda como
  cuestión abierta a resolver solo si el caso se materializa (ver Open questions).
  (Q2)
- **FR1.5** El arreglo DEBE afectar **únicamente al premio de ranking**
  (`ranking_prize`). El premio por puntos (`points_prize`), el MVP
  (`mvp_prize`) y el dream-team (`dream_team_prize`) NO se modifican, ya que no
  dependen de la posición relativa entre equipos. (Q1)

### FR2 — Conjunto de equipos premiables (sin cambios de criterio)

- **FR2.1** El sistema DEBE mantener el criterio actual de qué equipos entran al
  reparto de ranking: solo equipos "activos" (con puntos de jornada > 0) y, si el
  campeonato define `users_to_rank`, solo las posiciones premiadas. La regla de
  empate (FR1) se aplica dentro de ese conjunto premiable. (Q4)
- **FR2.2** En el campeonato de referencia todas las posiciones premian
  (no hay corte por `users_to_rank` que parta un grupo de empate), por lo que el
  caso de un grupo de empate que cruza el borde entre posiciones premiadas y no
  premiadas queda fuera del alcance verificado de este intent. (Q5)

### FR3 — Gating de jornada y aplicación retroactiva (sin cambios de gating)

- **FR3.1** El reparto de ranking (incluida la regla de empate) DEBE seguir
  aplicándose solo cuando la ronda está completa y cerrada
  (`award_round_prizes`), preservando el gating actual: jornadas con partidos
  aplazados o pseudo-jornadas adelantadas NO reparten premio de posición. El
  premio por puntos sigue pagándose de inmediato como hoy.
- **FR3.2** Al recalcular en el sync (que ya reprocesa todas las rondas), la
  corrección DEBE aplicarse **retroactivamente** a las jornadas pasadas afectadas
  por empates; la jornada 5 del campeonato de ejemplo debe quedar corregida tras
  el siguiente sync. (Q6)

## Requisitos no funcionales

- **NFR1 — Testabilidad / red de caracterización.** Antes de modificar la lógica,
  DEBE existir una red de tests de caracterización que congele el comportamiento
  observable actual de la producción del premio en `sync_prizes` en todas sus
  ramas (premio por puntos, gating de ronda completa, ranking flop/top, MVP,
  dream-team, jornada adelantada/negativa y el borrado defensivo
  `DELETE ... NOT IN`). El cálculo del reparto DEBE quedar en una función pura
  (sin I/O ni SQL) testeable de forma aislada. (team-practices, Q1 de
  practices-discovery)
- **NFR2 — No regresión.** La suite existente (incluida
  `test_finance_characterization.py`, que caracteriza el consumo) DEBE permanecer
  en verde. Los tests de caracterización que describan el comportamiento erróneo
  actual del reparto ante empates se retiran/actualizan de forma deliberada y
  trazable cuando el nuevo contrato lo sustituye.
- **NFR3 — Coste 0 €.** Los tests DEBEN ejecutarse con dobles/fakes de la API
  Futmondo y de la persistencia (patrón `conftest.py`), sin red real, sin
  `time.sleep()` y sin coste. Todo el trabajo se mantiene en tiers gratuitos.
- **NFR4 — Contención brownfield.** El cálculo puro extraído NO debe engordar el
  god-file `data_sync_service.py` ni introducir SQL en routers; `sync_prizes`
  pasa a orquestar (ingesta → cálculo puro → persistencia). El código nuevo de
  premios debe desambiguar el naming (`*_points` para métrica deportiva,
  `*_prize`/`*_amount` para importe).
- **NFR5 — Gate de CI.** El cambio DEBE pasar el gate bloqueante
  (gitleaks + `pytest` + `ng test`) antes de fusionar a `main`.

## Restricciones

- Stack fijo: Angular + FastAPI (Python 3.12) + Neon PostgreSQL + Fly.io; sin
  reescrituras grandes.
- La fórmula vive en el camino batch (`sync_prizes`), disparado por los crons de
  sync; la ruta de lectura (routers → `SELECT`/suma sobre `team_prizes`) no debe
  recalcular ni crecer.
- Coste 0 € (Neon free, Fly.io free allowance, GitHub Actions free).

## Supuestos

- El ranking de la ronda que devuelve la API incluye los puntos de jornada
  (`points`) por equipo, que son el criterio de empate. (soporta FR1.1)
- La fórmula de premio por posición vigente (`money_per_ranking * ratio` con
  `ranking_mode` flop/top y `total_pct`) es correcta para posiciones sin empate;
  el intent solo corrige la agregación/reparto entre empatados, no la fórmula por
  posición. (soporta FR1.2/FR1.3)
- El recálculo total en cada sync es intencional y deseado; no se congela lo ya
  repartido. (soporta FR3.2)

## Fuera de alcance

- La doble semántica de "puntos" (métrica deportiva vs importe) y la resolución
  de identidad por nombre en `player_finances`: se documentan como deuda conocida
  y NO se modifican en este intent. (Q6 de practices-discovery)
- Cambios en MVP, dream-team, premio por puntos o en el gating de ronda completa.
- Paridad del job `verify` (push→`main`) con el gate de PR respecto a `--cov`:
  diferido a un futuro diseño de pipeline.
- Cambios en la ruta de lectura (routers de finanzas/balances/analytics).

## Open questions

- **OQ1** Reparto exacto del resto cuando `suma_posiciones / N` no es entero:
  se ha decidido redondear cada parte con `round()` (FR1.4) por no conocerse con
  certeza cómo cuadra Futmondo el resto. Si aparece un caso real de división no
  entera, decidir entonces la regla de cuadre (repartir el resto, truncar, etc.).
  La caracterización debe registrar qué hace Futmondo si se observa tal caso.

## Assumptions & Open Questions

Ver secciones "Supuestos" y "Open questions" arriba. Ninguna incertidumbre
bloquea la generación de historias de usuario; OQ1 se resolverá solo si el caso
de división no entera se materializa.
