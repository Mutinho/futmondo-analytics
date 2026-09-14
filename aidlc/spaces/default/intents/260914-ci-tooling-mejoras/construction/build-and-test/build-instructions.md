# Instrucciones de Build — Mejoras de CI/Tooling

> Etapa Build and Test (Construction) · Intent `260914-ci-tooling-mejoras` · Scope `refactor` · Estrategia de test: Minimal.
> Consume: `code-generation-plan.md`, `unit-test-instructions.md`, `code-summary.md`.

## Contexto

Trabajo de mantenimiento de CI/tooling (5 mejoras). No hay build de negocio nuevo; el "build" relevante es el del frontend Angular (que además valida la migración Karma→Vitest) y la coherencia de los workflows de CI. El backend (FastAPI) no se toca en este intent.

## Prerrequisitos

- **Node ≥ 22.22.3** (Angular CLI 22 lo exige; fijado en `.nvmrc`). Si el Node local es inferior, usar contenedor `node:22.22.3` (ver más abajo).
- **npm 11+** (declarado en `package.json` como `packageManager: npm@11.12.1`). El npm 9.x del sistema falla al resolver el árbol de Angular 22/Vitest 4.
- Docker disponible si se usa la vía en contenedor.

## Instalación de dependencias

Frontend:

```bash
cd angular-app && npm ci
```

El `package-lock.json` está regenerado sin el stack de Karma, con `vitest@^4.0.8` y `jsdom@^25.0.1`.

## Comandos de build

Build de producción del frontend (verificación de que la app sigue compilando):

```bash
cd angular-app && npx ng build
```

## Verificación del build (con la versión de Node correcta)

Si el Node local es < 22.22.3, ejecutar en contenedor efímero (coste 0€):

```bash
docker run --rm \
  -v "$PWD/angular-app":/app -w /app \
  -v /app/node_modules \
  node:22.22.3 \
  bash -c "npm ci && npx ng build"
```

## Verificación de los workflows de CI (mejoras 1 y 4)

- `.github/workflows/ci.yml` y `.github/workflows/fly-deploy.yml`: comprobar que `actions/setup-node@v5`, sin `--browsers=ChromeHeadless` ni paso `setup-chrome`, y sin `ACTIONS_ALLOW_USE_UNSECURE_NODE_VERSION`.
- La ejecución real de los workflows la realiza GitHub Actions al abrir PR / push a `main`.

## Troubleshooting

- **`edgesOut` / fallo de `npm install` con npm 9.x**: usar npm 11 (`corepack npm@11.12.1 ...`) o el contenedor `node:22.22.3`.
- **`Angular CLI requires a minimum Node.js version of v22.22.3`**: el Node local es inferior; usar el contenedor.
- **`A DOM environment is required`**: falta `jsdom` (ya añadido como devDependency); reinstalar con `npm ci`.
