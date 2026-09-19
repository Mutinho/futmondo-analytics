# Units Generation — Preguntas de descomposición

Intent: `frontend-coverage-gate` (scope `classic`, brownfield). Intervención acotada y secuencial (FR10 → FR17.1) sobre infraestructura de tests del frontend + pipeline. Este stage produce la topología de unidades (el DAG); la secuencia económica la decide Delivery Planning (2.9).

## Q1 — Granularidad de la descomposición en unidades

El trabajo es una intervención cohesiva y secuencial: FR10.1 (retirar `skipTests`) → FR10.2 (infraestructura de cobertura + siembra P0) → FR17.1 (cablear el gate en ci.yml y verify), con un orden obligado. ¿Cómo lo descomponemos en unidades de trabajo?

- A. **Una sola unidad** `frontend-coverage-gate` que abarca FR10.1 + FR10.2 + FR17.1. El orden interno (FR10 → FR17.1) se maneja como secuencia dentro de la unidad; no hay paralelismo útil que justifique dividir (la config de cobertura, la siembra y el cableado del gate están fuertemente acoplados en `angular.json`/`ng test`). (recomendado)
- B. Dos unidades: (U1) cobertura de tests del frontend (FR10) y (U2) cableado del gate en el pipeline (FR17.1), con U2 dependiendo de U1.
- C. Tres unidades (una por FR10.1, FR10.2, FR17.1).
- X. Other (please specify)

[Answer]: A

## Q2 — Kind de la unidad (tipo de artefactos de diseño que arrastra a Construcción)

¿Qué tipo mejor describe lo que ES esta unidad?

- A. **`packaging`** — build/distribución/config y tooling: `angular.json` (schematics, target `test`, cobertura), devDependency del proveedor, specs de test sembrados y workflows de CI (`ci.yml`, `verify`). No es un servicio desplegable, ni una UI, ni una librería reutilizable. (recomendado)
- B. `library` — código reutilizable sin runtime propio.
- C. `service` — un ejecutable desplegable.
- X. Other (please specify)

[Answer]: A

---

## Consolidated Summary Confirmation

- Looks correct
- Request changes

[Answer]: Looks correct