# Requirements Analysis — Preguntas de clarificación

Intent: `261005-data-manager-god-file` — Refactor del god-file
`backend/app/services/data_manager_v2.py` (clase única `DataManagerV2`, 3692
líneas / 57 métodos) al patrón DDD ya probado, characterization-first estricto,
preservando la superficie pública exacta. Profundidad: **Minimal**.

> Las opciones etiquetadas (A–E, X) son el registro autoritativo del fichero.
> En la presentación interactiva se renumeran como prosa; respondes por el
> número mostrado, no por la letra.

---

## Q1 — Criterio de equivalencia funcional estricta (pass/fail del characterization)

La descripción pide "equivalencia funcional estricta sin cambio de comportamiento
observable". Para que cada extracción tenga un criterio pass/fail verificable,
¿cómo se demuestra que una responsabilidad extraída es equivalente al original?

- A. **Characterization tests por responsabilidad ANTES de extraer** (congelar el
  comportamiento observable de los métodos de esa responsabilidad con los fakes
  in-memory de `conftest.py`), y que esos mismos tests sigan en verde tras la
  extracción. La superficie pública (nombres/firmas de los 57 métodos +
  constructor `skip_init=True`) se preserva byte-a-byte. (Recomendada: alinea con
  el mandato afirmado characterization-first y con las oleadas previas.)
- B. Como A, pero además exigir que la **suite completa de `backend/tests/`** siga
  en verde (no sólo los tests de la responsabilidad) en cada paso.
- C. Sólo verificar que la suite existente no se rompe, sin añadir characterization
  nuevo por responsabilidad.
- D. Verificación manual / revisión de diff, sin tests nuevos.
- X. Other (please specify)

[Answer]: A

---

## Q2 — Deuda de manejo de errores y puntos de corrupción (alcance en ESTE refactor)

El escaneo encontró en el god-file: 18 `except Exception` + 5 `except:` desnudos,
16 `return None`, y un punto de reemplazo de conjunto con riesgo de corrupción
(`delete_orphan_players`, `DELETE ... NOT IN` sin transacción compartida con los
upserts previos). ¿Qué alcance tiene este refactor sobre esa deuda?

- A. **Preservar el comportamiento observable tal cual** al extraer (no cambiar
  excepts ni señales de fallo); la deuda de error-handling y los puntos de
  corrupción quedan **registrados como deuda** (open questions / out-of-scope)
  para un intent futuro. El refactor es equivalencia estricta, no endurecimiento.
  (Recomendada: mantiene el blast radius mínimo y respeta "sin cambio de
  comportamiento observable".)
- B. Preservar error-handling, pero **elevar los reemplazos de conjunto** (p. ej.
  `delete_orphan_players`) al patrón atómico de referencia (`team_prizes_writer`)
  como parte de este refactor, por ser riesgo de corrupción de datos.
- C. Sanear también la deuda de error-handling (tipar fallos, distinguir
  `Optional` de fallo silencioso) dentro de este refactor.
- D. B + C (elevar corrupción Y sanear error-handling).
- X. Other (please specify)

[Answer]: A

---

## Q3 — Destino de los adapters DDD existentes y del SQL-en-router de los consumidores

Hoy 4 oleadas DDD (`analytics/`, `assistant/`, 10 contextos `sync/*`, `prizes/`)
envuelven `DataManagerV2` **verbatim** desde su `infrastructure/*_adapter.py`, y
hay SQL-en-router en los 8 routers consumidores. Al descomponer el god-file,
¿qué pasa con esos consumidores?

- A. **No tocar los consumidores**: los adapters existentes y los routers siguen
  invocando la misma superficie pública de `DataManagerV2`, que ahora es un facade
  delgado que delega en los módulos extraídos. El SQL-en-router existente queda
  **como deuda registrada**, no se amplía ni se retira en este intent.
  (Recomendada: regla afirmada NEVER ampliar god-files ni SQL-en-router; preserva
  el contrato byte-a-byte.)
- B. Como A, pero además **retirar el SQL-en-router** de los 8 routers consumidores
  llevándolo tras los nuevos módulos de infraestructura en este mismo intent.
- C. Re-cablear los adapters DDD existentes para que apunten a los nuevos módulos
  extraídos en vez de a la superficie del facade.
- X. Other (please specify)

[Answer]: A

---

## Q4 — Granularidad del inventario de responsabilidades para Plan Approval

El escaneo agrupó los 57 métodos en ~14 responsabilidades candidatas (players,
teams/standings, performance, transactions, clauses, punishments/bonuses,
dream-teams/MVP, prizes, market/roster, match-odds, news/articles,
users/stats/evolution, sync-metadata/cache, schema/lifecycle). La descripción
dice que el inventario y el orden de extracción (de menor a mayor acoplamiento)
**se confirman en Plan Approval**. ¿Qué granularidad quieres que fije el
requisito?

- A. **Un módulo DDD extraído por responsabilidad** (≈14 unidades), extraídas de
  menor a mayor acoplamiento, cada una characterization-first → extraer → verde.
  El inventario y el orden exactos se cierran en Plan Approval. (Recomendada:
  granularidad fina = rollback quirúrgico por responsabilidad, igual que las
  oleadas de sync.)
- B. Agrupar responsabilidades afines en menos módulos (p. ej. ~6–8) para reducir
  el número de pasos.
- C. Un único módulo de acceso a datos extraído (descomposición mínima).
- X. Other (please specify)

[Answer]: A

---

## Consolidated Summary Confirmation

Resumen de las decisiones tomadas (todas en modo guiado):

- Q1 — Equivalencia estricta vía **characterization tests por responsabilidad
  ANTES de extraer** (fakes in-memory de `conftest.py`) que siguen en verde tras
  extraer; superficie pública (constructor `skip_init=True` + 57 métodos)
  preservada byte-a-byte. (A)
- Q2 — **Preservar el comportamiento observable tal cual**: no se tocan excepts ni
  señales de fallo; la deuda de error-handling (18 `except Exception`, 5 `except:`
  desnudos, 16 `return None`) y los puntos de corrupción (`delete_orphan_players`)
  quedan **registrados como deuda / out-of-scope** para un intent futuro. (A)
- Q3 — **No tocar los consumidores**: la superficie de `DataManagerV2` pasa a ser
  un facade delgado que delega en los módulos extraídos; los adapters DDD
  existentes y los 8 routers siguen invocándola igual. El **SQL-en-router**
  existente queda **como deuda registrada** (ni se amplía ni se retira). (A)
- Q4 — **Un módulo DDD extraído por responsabilidad** (≈14 unidades), de menor a
  mayor acoplamiento, cada una characterization-first → extraer → verde; el
  inventario y el orden exactos se cierran en **Plan Approval**. (A)

Restricciones arrastradas de la descripción y las reglas afirmadas (no se
re-preguntan): coste 0 €; patrón DDD probado (facade → orchestrator → domain
`Protocol` port sin SQL → `infrastructure/*_adapter` que envuelve SQL verbatim);
sin reformateo masivo (`ruff format` sólo quirúrgico en ficheros nuevos); sin
relajar el piso `--cov-fail-under` (sólo sube por trinquete); identificadores/
docstrings/comentarios en INGLÉS, texto de usuario/commits en CASTELLANO.

Does this all look correct before I generate the requirements artifact?

- Looks correct
- Request changes

[Answer]: Looks correct
