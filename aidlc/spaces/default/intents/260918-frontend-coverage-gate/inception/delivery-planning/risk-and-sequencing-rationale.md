# Riesgo y Racional de Secuenciación — Frontend Coverage Gate

## Secuencia de Bolts

Un único Bolt (una sola unidad de trabajo), así que **no hay decisión de secuencia externa entre Bolts** ni ruta crítica multi-Bolt que justificar. El DAG de unidades (`unit-of-work-dependency.md`) es un único nodo con `depends_on: []`; el plan de Bolts lo respeta trivialmente (no hay desviación del orden topológico).

## Racional del orden INTERNO del Bolt (risk-first)

Aunque la secuencia externa es trivial, el orden **dentro** del Bolt sí es una decisión, y se resuelve **risk-first** (heurística de reducción de riesgo primero, en línea con el argumento de Reinertsen sobre atacar la incertidumbre temprano):

1. **Spike de cableado/medición primero (Q1=A)** — el mayor riesgo del intent son los supuestos técnicos:
   - **A2**: que el builder `@angular/build:unit-test` de Angular 22 acepte las opciones `coverage.*` (`provider`, `all`, `include`, `exclude`, `thresholds`) en las `options` del target `test` de `angular.json`. Si fuese falso, chocaría con la restricción C2 (fuente única en `angular.json`).
   - **A3**: que activar el umbral dentro de `ng test` propague el enforcement a `ci.yml` (PR) y al job `verify` de `fly-deploy.yml` (push→`main`) sin tocar la cadena `needs:`.
   Validar ambos con un spike barato antes de sembrar en masa evita rework si un supuesto no se sostiene.
2. **FR10.1** (retirar `skipTests` de schematics de lógica) — cambio de bajo riesgo, habilita que el código nuevo nazca con spec.
3. **FR10.2** (provider a versión fijada + config de cobertura con denominador estable + umbrales por métrica).
4. **FR10.3** (siembra P0 `auth.guard` + `auth.service`, luego P1/P2) — antes de activar el umbral bloqueante, para no romper el gate.
5. **Medir base y fijar el umbral por debajo** — estabilidad del gate (NFR3).
6. **FR17.1** (cablear el comando `ng test` con cobertura en `ci.yml` y `verify`) — el gate solo tiene sentido cuando existe el umbral; orden obligado FR10 → FR17.1.

No se usa un modelo de puntuación formal (WSJF/CD3): con un único Bolt no hay ranking que calcular. La heurística aplicada es **risk-first para el orden interno** + **orden obligado FR10 → FR17.1** por dependencia funcional.

## Riesgos y mitigaciones

| Riesgo | Impacto | Mitigación |
|--------|---------|------------|
| A2 falso (builder no lee `coverage.*` del target `test`) | Alto (rompe la fuente única C2) | Spike inicial; si falla, decidir alternativa de cableado en diseño sin salir de `angular.json` |
| A3 falso (enforcement no se propaga al gate) | Alto (FR17.1 no se cumple) | Spike valida el comando exacto en ambos workflows antes de sembrar |
| Umbral inicial rompe el gate al activarlo | Medio | Medir base tras siembra P0 y fijar por debajo (colchón 2–5 pts), por métrica (NFR3) |
| Cambio de devDependency rompe `npm ci`/`ng test` en CI | Medio | Verificar en `node:22.22.3` antes de pushear (NFR5, regla dura Q7-B) |
| Tests-espejo sin aserciones (falsa significatividad) | Medio | Cobertura por métrica (`branches`/`functions`) + revisión humana en MR (FR17.1.1) |

## Assumptions & Open Questions

- El valor exacto del umbral se determina en implementación tras medir la base.
