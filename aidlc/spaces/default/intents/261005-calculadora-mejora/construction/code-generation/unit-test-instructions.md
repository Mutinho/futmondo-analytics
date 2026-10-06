# Unit Test Instructions — calculator-toggle

## Framework y configuración

- Runner: Angular `ng test` con builder `@angular/build:unit-test` + Vitest
  (`vitest 4.1.11`, `@vitest/coverage-v8 4.1.11`, `jsdom`). Umbrales de
  cobertura por métrica en `angular.json` (`coverageThresholds`); el ratchet
  solo sube. Node `22.22.3` (`.nvmrc`).
- Sin dependencias de test nuevas: `MatSlideToggleModule` ya viene con
  `@angular/material` (dependencia existente).

## Comando unit-scoped (SOLO este componente)

Desde `angular-app/`, ejecutar únicamente el spec de la Calculadora:

```bash
cd angular-app && npx ng test --include "src/app/features/calculator/calculator.component.spec.ts"
```

(Comando acotado a ESTE fichero; nunca el `ng test` global del proyecto. Si el
Node local no alcanza el mínimo del Angular CLI, correr en contenedor
`node:22.22.3` con volumen anónimo para `node_modules`, a coste 0 €.)

El runner Vitest ya es ejecutable con la config existente (no se bootstrapea
nada nuevo); este comando debe correr antes del primer test.

## Alcance (estrategia Minimal, scope refactor)

Un test por requisito al nivel más estrecho (unit de componente), con piso
happy-path. ~5–8 specs en total para esta unidad:

1. Characterization: `futureBalance` actual (equivalente a ON) =
   `balance + selectedTotal + onSaleTotal - activeBidsTotal`, y lista
   seleccionable actual (excluye los jugadores en venta).
2. Toggle ON incluye `onSaleTotal` y excluye los jugadores en venta de la lista (FR1.2/BR1.1, FR5.1/BR5.1).
3. Toggle OFF excluye `onSaleTotal`, incluye esos jugadores en la lista deseleccionados y oculta el bloque "En venta" (FR1.3/BR1.2, FR5.2/FR5.3/BR4.1/BR5.2).
4. `activeBidsTotal` resta en ON y en OFF (FR2.1/BR2.1).
5. Invariante anti-doble-conteo: con OFF, seleccionar un ex-onSale suma a `selectedTotal` por una sola vía (FR5.5/BR5.4).
6. Transición OFF→ON re-excluye los jugadores en venta y limpia su selección manual (FR5.4/BR5.3).
7. Cambiar el toggle persiste en `localStorage['futmondo_calc_include_onsale']` (FR3.1/BR3.1).
8. Restauración desde `localStorage` al inicializar: `'true'`→ON, `'false'`→OFF (FR3.2/BR3.2).
9. Fallback a ON ante clave ausente o valor corrupto/no booleano (FR3.3/FR3.4/BR3.3/BR3.4).

## Cobertura objetivo

Mantener la suite existente verde; subir (nunca bajar) los umbrales de
`angular.json` al valor medido tras añadir el spec. Sin asserts espejo ni
`assert`/`expect(true)`; cada test asevera el efecto (valor de `futureBalance`
o estado de `localStorage`).

## Mocking / stubbing

- Mockear `localStorage` (jsdom lo provee; limpiar entre tests con
  `localStorage.clear()` en `beforeEach`).
- Stubear/espiar los servicios HTTP (`RosterService`, `HttpClient`,
  `ChampionshipService`) para fijar `balance`, `onSalePlayers`, `activeBidsTotal`
  y la selección sin red ni backend real.
- Sin credenciales ni tokens reales (gitleaks escanea `*.spec.ts`).

## Gestión de datos de test

Datos sintéticos en el propio spec (jugadores y totales fijos); sin fixtures
externas ni BD.
