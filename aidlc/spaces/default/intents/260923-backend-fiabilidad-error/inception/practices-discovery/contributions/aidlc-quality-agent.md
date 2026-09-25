**Collaborator:** aidlc-quality-agent

## Contribution

Reviso el borrador del lead desde la posture de testing, el tooling de cobertura,
los gates de CI y los patrones de test para la taxonomía recuperable/fatal de este
intent de fiabilidad (FR3.2 + FR4). La base afirmada (test-after + characterization-first,
coste 0 €, gate CI bloqueante, sin bajar cobertura) está bien arrastrada y es
consistente con la evidencia. Señalo los huecos que la entrevista humana debe cerrar.

1. **Asimetría de cobertura `--cov` diferida vs. la ambición de FR3.2/FR4 — pedir
   decisión explícita, no sólo "deuda registrada".** El borrador clasifica como deuda
   fuera de alcance que `verify` (`fly-deploy.yml`) corra `pytest -q` **sin `--cov`**
   mientras `ci.yml` mide `--cov=app`. Es correcto que la asimetría preexista, PERO este
   intent introduce **caracterización nueva de rutas críticas** (`_make_request`, punto de
   corromper-datos, ramas recuperable/fatal). El riesgo real: esa nueva caracterización
   sólo se **mide** en el camino PR (`ci.yml`), no en el push→`main` (`verify`). Como HOY
   no hay `cov-fail-under` en ninguno de los dos, la asimetría es sólo de *señal* y no
   rompe nada — pero la entrevista debe **confirmar** que este intent NO introduce piso de
   cobertura backend (mantener el ratcheting diferido), porque si lo introdujera, cablearlo
   sólo en `ci.yml` dejaría el push directo a `main` sin enforcement. Gap para la
   entrevista: "¿este intent mantiene el `--cov` como observabilidad-only sin piso, o
   introduce un piso, y en ese caso en AMBOS caminos?".

2. **Ordering del characterization-first: falta el criterio de "verde en cada paso"
   como puerta, no como nota.** El borrador dice "con la suite existente en verde en cada
   paso", lo cual es correcto y alineado con el mandato afirmado. Pero para FR4 (cambio de
   contrato de `_make_request` de `None`/`bool` a excepción tipada, blast radius alto sobre
   el god-file de 1915 líneas) el orden operativo debe ser explícito en la posture: (a)
   caracterizar el contrato ACTUAL (`None`/`bool` por modo de fallo) con fakes en memoria;
   (b) mapear e inventariar los llamadores `sync_*`/`get_*` que asumen `None == sin datos`;
   (c) sólo entonces introducir la excepción tipada + actualizar llamadores; (d) los specs
   de los llamadores deben re-verificar que el nuevo modo de fallo se propaga o se degrada
   correctamente, no sólo que "no explota". La entrevista debe validar que el paso (b)
   —inventario de llamadores— es una entrega verificable y no un supuesto.

3. **Piso de aserción significativa: definir qué distingue un spec de "typed-exception
   detection" real de uno espejo.** El borrador prohíbe `assert True` (bien), pero para
   esta taxonomía conviene un piso concreto que la reviewer/CI pueda exigir: un spec de
   modo de fallo recuperable debe aseverar (i) que el `StepStatus.DEGRADED` se marca vía
   `sync_step_status.py` y (ii) que la operación NO falla; un spec de modo fatal debe
   aseverar (i) que la excepción tipada se propaga (`pytest.raises(<Typed>)`) y (ii) que
   NO deja datos a medias (estado de la caché/tabla verificado tras el fallo). El
   anti-patrón concreto a prohibir aquí no es `assert True` sino el **spec que sólo captura
   la excepción sin aseverar el efecto lateral** (o su ausencia). Sugiero que la posture lo
   nombre explícitamente. Es la brecha de *meaningfulness*, análoga a la de FR17.1 del
   intent previo, trasladada al backend.

4. **Test del punto de corromper-datos: exigir aserción del estado tras fallo del
   `DELETE`.** El `DELETE FROM team_prizes ... NOT IN (...)` (L1846) tras `commit()` previo
   (L1825) con `try/except → logger.warning` (L1859) es el hallazgo propietario de mayor
   riesgo. El spec de caracterización DEBE congelar el comportamiento actual (caché en
   estado mixto tras fallo del DELETE, sin señal al consumidor) ANTES de endurecer hacia el
   reemplazo transaccional atómico, y el spec post-endurecimiento debe aseverar atomicidad
   (o todo o nada). El fake `_FakeInMemoryDB`/`_FakeCursor` de `conftest.py` debe poder
   simular el fallo del `DELETE` de forma determinista; la entrevista/diseño debe confirmar
   que el fake lo soporta o qué doble adicional se necesita (sin red, sin DB real).

5. **`E722` por trinquete: el enforcement no es medible con `ruff check` advisory
   `continue-on-error`.** El borrador propone re-habilitar `E722` por trinquete (bien y
   necesario, es la causa raíz de por qué la deuda pasó desapercibida). Pero desde calidad
   señalo un matiz: `ruff check` es **advisory** (`continue-on-error`) en CI, así que
   re-habilitar `E722` NO lo convierte en gate bloqueante por sí solo — un `except:` desnudo
   nuevo seguiría pasando el merge. Si el objetivo de FR3.2 es *impedir* nuevos bare-except,
   la entrevista debe decidir si (a) basta con el enforcement advisory + revisión humana, o
   (b) `E722` debe promoverse a bloqueante (quitando `continue-on-error` sólo para esa regla,
   o vía un check dedicado). Es una decisión de gate, no de estilo, y hoy queda ambigua.

6. **Cobertura existente que ancla la caracterización — reutilizar, no duplicar.** La
   evidencia confirma specs de referencia ya verdes que fijan los patrones a replicar:
   `test_sofascore_sync_characterization.py` (reemplazo transaccional atómico +
   `SofascoreIPBanError`), `test_sync_degraded_steps.py`/`test_sync_step_status.py`
   (`StepStatus.DEGRADED`), `test_durable_task_*` (autoridad DB vs best-effort). La posture
   debería citar estos como patrón-plantilla obligatorio para los specs nuevos, para que la
   taxonomía recuperable/fatal se implemente de forma consistente con lo ya caracterizado y
   no reinvente el doble/fake. El borrador lo menciona parcialmente; conviene hacerlo
   explícito en el Ordering.

## Positions

- AGREE: La posture test-after + characterization-first arrastrada es correcta y la extensión a los broad-except FR3.2 y al contrato de `futmondo_client._make_request` está bien justificada por el blast radius alto y el mandato afirmado.
- AGREE: Tratar la asimetría `--cov` (`verify` sin `--cov` vs `ci.yml` con `--cov=app`) como deuda diferida es defendible mientras no exista piso de cobertura; hoy es señal, no seguridad (gitleaks bloquea en ambos caminos).
- AGREE: Re-habilitar `E722` por trinquete aislando el reflow de la regla de NO reformatear brownfield en masa es la corrección mecánica correcta y trazable a la evidencia.
- OBJECT: La posture no fija un piso de aserción significativa específico para modos de fallo (propagación de excepción tipada + efecto lateral verificado); sin él, un spec espejo que sólo hace `pytest.raises` sin aseverar estado pasaría, replicando la brecha de meaningfulness de FR17.1 en el backend.
- OBJECT: Re-habilitar `E722` NO garantiza enforcement porque `ruff check` es advisory (`continue-on-error`); la entrevista debe decidir si el bare-except nuevo debe *bloquear* el merge o basta con advisory + revisión, hoy queda ambiguo.
- OBJECT: El Ordering no exige el inventario/mapeo de llamadores de `_make_request` como entrega verificable previa al cambio de contrato; dado el god-file de 1915 líneas es el mayor riesgo de regresión de FR4 y debe ser un paso explícito, no un supuesto.
