# Build Instructions — frontend-coverage-gate

Intent `260918-frontend-coverage-gate` (scope `classic`, brownfield, frontend-only). Intervención acotada y aditiva sobre `angular-app/` y los workflows de CI. Estrategia de test **standard**, metodología **test-after**.

## Alcance del build

Este intent NO añade componentes ni servicios de negocio: añade infraestructura de cobertura (`@vitest/coverage-v8`), config de cobertura en el target `test` de `angular.json`, 12 specs sembrados y el cableado del umbral en los workflows. El "build" relevante es el del frontend Angular; el backend queda inalterado.

## Requisitos previos

- **Node** `22.22.3` (`.nvmrc`, alineado con la línea Node 22 de CI). Si el Node local no alcanza, usar contenedor `node:22.22.3` con volumen anónimo para `node_modules` (coste 0 €).
- `npm@11.12.1` (campo `packageManager` de `angular-app/package.json`).

## Instalación de dependencias

```bash
# desde angular-app/ (o en contenedor node:22.22.3):
npm ci
```

`npm ci` instala desde `package-lock.json` (regenerado para incluir `@vitest/coverage-v8@4.1.11` exacto, casado en major con `vitest@4.1.11`).

## Comando de build

El builder de test compila el bundle de la app antes de ejecutar la suite; no hay un paso de build separado obligatorio para este intent. Para validar el bundle de producción de forma independiente:

```bash
npx ng build --configuration development
```

## Verificación del build

- `npm ci` termina sin errores de resolución/lock.
- `npx ng test --watch=false` arranca el builder `@angular/build:unit-test` (runner Vitest), compila el bundle ("Application bundle generation complete") y ejecuta la suite con cobertura V8.

## Contenedor de verificación (coste 0 €)

```bash
docker run --rm -v "$PWD/angular-app":/app -v /app/node_modules -w /app node:22.22.3 \
  bash -lc 'npm ci && npx ng test --watch=false'
```

Tras verificar, borrar el cache transitorio `angular-app/.angular/` (gitignored; el motor lo trata como fuente si permanece).

## Troubleshooting

- **`EBADENGINE`**: Node local por debajo de 22.22.3 → usar el contenedor.
- **Mismatch de major Vitest/coverage-v8**: la instrumentación V8 rompe si `@vitest/coverage-v8` no casa en major con `vitest`; ambos fijados a `4.1.11`.
- **`PARSE_ERROR` de V8 sobre `.html`/`.scss`**: `coverageInclude` está acotado a `src/app/**/*.ts` a propósito para evitarlo.
- **Fichero `angular-app/.angular/**` marcado como fuente sin reclamar (RFC #662)**: es cache de build regenerable; borrarlo antes de cerrar el gate.
