# Build Instructions — calculadora-mejora

Cambio frontend-only (Angular) sobre `angular-app/`. Coste 0 €.

## Dependencias

- Node `22.22.3` (`.nvmrc`). El Angular CLI exige ese mínimo; si el Node local
  es inferior, usar contenedor `node:22.22.3` con volumen anónimo para
  `node_modules` (práctica afirmada, coste 0 €).
- Sin dependencias nuevas: `MatSlideToggleModule` ya viene con `@angular/material`.

```bash
cd angular-app && npm ci
```

## Entorno

- No requiere variables de entorno nuevas para build/test del frontend.
- El toggle usa `localStorage` (navegador); en tests, jsdom lo provee.

## Build

```bash
cd angular-app && npx ng build        # producción (bundle)
```

(En CI, el build de producción corre en `fly-deploy.yml`; para esta mejora el
gate relevante es `ng test`, que compila y ejecuta la suite.)

## Verificación del build

- `ng test` compila el proyecto y ejecuta la suite Vitest; un fallo de
  compilación aborta la ejecución.

## Troubleshooting

- **EBADENGINE / Angular CLI exige Node ≥ 22.22.3**: ejecutar en contenedor
  `node:22.22.3` (ver arriba).
- **502 de nginx en el stack Docker local tras rebuild**: es el proxy con IPs de
  upstream cacheadas; recrear con `docker compose up -d --force-recreate`
  (incidencia de orquestación local, no del código).

## Sources

- `code-generation/code-generation-plan.md`, `code-summary.md`.
- `.nvmrc`, `angular-app/package.json`, `angular-app/angular.json`.

## Assumptions & Open Questions

None.
