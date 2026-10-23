# Interaction Spec — F2: Presupuesto nativo + selector de campeonato

> Fase: inception (refined-mockups). Idioma: castellano; tokens técnicos verbatim en inglés.

## Selector de campeonato (navigation bar)

- **Trigger**: toque sobre el título (nombre del campeonato activo + chevron) en la navigation bar.
- **Despliegue**: `Menu` nativo con la lista de campeonatos; el activo con ✓.
- **Selección**: al elegir, se cierra el menú, se persiste en `UserDefaults`, y la pantalla entra en estado de carga y recarga el presupuesto del nuevo campeonato.
- **Deshabilitado**: si la lista de campeonatos está vacía, el título no es interactivo.

## Ordenación

- **Trigger**: botón "⇅ Ordenar" en la navigation bar → `Menu` con las 6 claves (saldo, rendimiento, puja máxima, valor plantilla, gastado, ingresado); la clave activa con ✓.
- **Comportamiento**: orden **sólo descendente** por la clave elegida (decisión FR2.1); el toggle ascendente/descendente queda **diferido** (follow-up). Reordena in-place con animación nativa.
- **Nota (clave no visible)**: el menú ofrece 6 claves de orden aunque la fila muestre 4 métricas; ordenar por una clave no visible (`team_value`, `total_spent`, `total_income`) es **intencional** y coherente con FR2.1 — permite reordenar por un criterio sin saturar la fila; el valor de esa clave se ve en el detalle diferido.

## Carga / error / vacío

- **Carga**: indicador aparece <100 ms al iniciar la carga (incluido el cambio de campeonato) y desaparece al llegar datos/error.
- **Error**: mensaje + [Reintentar]; reintentar relanza la carga; el campeonato activo persistido no se altera por un fallo.
- **Vacío**: `teams[]` vacío → estado vacío (no error); lista de campeonatos vacía → mensaje + selector deshabilitado.

## Sources

- `aidlc/spaces/default/intents/261019-presupuesto-selector-cam/inception/requirements-analysis/requirements.md` (FR2.1, FR3, FR4)
- `aidlc/spaces/default/intents/261019-presupuesto-selector-cam/ideation/rough-mockups/user-flow.md`

## Assumptions & Open Questions

None.
