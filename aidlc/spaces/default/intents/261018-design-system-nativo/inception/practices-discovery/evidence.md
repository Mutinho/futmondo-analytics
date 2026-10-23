# Evidence — Practices Discovery (RE-RUN / DRAFT)

Intent: `261018-design-system-nativo` (sistema de diseño / theming nativo iOS en
SwiftUI reproduciendo el tema del frontend Angular).
Modo: subagent, **LEAD-ONLY** (collaborators off; no hay spokes).
Lead: `aidlc-pipeline-deploy-agent`.

## Qué inspeccioné

### Memoria afirmada (baseline — leída, NO reescrita)
- `aidlc/spaces/default/memory/team.md` — secciones `## Way of Working`,
  `## Walking Skeleton`, `## Testing Posture`, `## Deployment`, `## Code Style`.
  Todas pobladas (no vacías): trunk-based + squash a `main`, gate de CI
  obligatorio replicado en `ci.yml` (job `quality`) y `fly-deploy.yml` (job
  `verify`), walking skeleton OFF (sistema en producción), testing posture
  **test-after** con suite characterization-first y trinquete de cobertura que
  sólo sube, deploy on-merge a Fly.io con smoke `/health`, coste 0 € con la
  excepción acotada de Apple Developer Program, idioma inglés en código /
  castellano en UI y commits.
- `aidlc/spaces/default/memory/project.md` — `## Mandated`, `## Forbidden`,
  `## Corrections`. Constraints duros ya estampados: coste 0 €, no credenciales
  en claro, `JWT_SECRET` no-default, no ampliar god-files, no `ruff format`
  masivo, ratchet sólo sube, gitleaks escanea specs. En `## Corrections`:
  reproducir en SwiftUI el tema de Angular como fuente de verdad del diseño
  nativo con **Google Stitch descartado** (learned 2026-10-18).

### Evidencia codekb (recién publicada, run 261018)
- `technology-stack.md` — confirma el stack: backend FastAPI/Python 3.12 +
  `pytest`/`pytest-cov`, frontend Angular 22 + Material 3 + Vitest `4.1.11` +
  `@vitest/coverage-v8` + `jsdom`; theming Material 3 (`mat.theme`,
  `mat.$green-palette` primaria / violeta terciaria, `Roboto`, tokens
  `--mat-sys-*`, tokens semánticos propios, modo claro/oscuro, gradiente splash).
  El target nativo es SwiftUI + SDK de Apple; donde Material 3 no tenga 1:1 se
  cubre con Apple HIG. Google Stitch descartado.
- `code-quality-assessment.md` — confirma el **gate de CI bloqueante operativo**
  en ambos workflows, pisos de cobertura heredados (backend 27; frontend
  19/19/17/18) con ratchet sólo-sube, suite backend characterization-first y
  frontend Vitest; y explícitamente que el arnés Vitest/jsdom **no porta 1:1** a
  un target nativo (el arnés de UI se rehace — riesgo a documentar).
- `business-overview.md` — confirma que este intent es de **diseño visual** sin
  cambios de backend ni de datos; fuente de verdad = tema de Angular; Stitch
  descartado.
- (También consultados de pasada: `code-structure.md`, `architecture.md`,
  `dependencies.md` existen en el codekb y son coherentes con lo anterior.)

### Persona / plantilla / knowledge
- Persona `aidlc-pipeline-deploy-agent` y knowledge compartido/propio
  (`rules-reading.md`, `branching-strategies.md`, `cicd-patterns.md`).
- Plantilla de etapa `.kiro/aidlc-common/stages/inception/practices-discovery.md`
  (Step 5 define el contenido exacto de los 4 artefactos y los campos
  obligatorios de `## Testing Posture`).

## Inferencias
- Es un proyecto brownfield **maduro y en producción**; la evidencia codekb
  corrobora 1:1 lo ya afirmado en memoria. No hay señales de que ninguna práctica
  haya cambiado.
- El único delta real que aporta este intent es el **matiz nativo iOS/SwiftUI**:
  (a) la UI SwiftUI no usa el arnés Vitest/jsdom del frontend Angular (no porta
  1:1; el toolchain de verificación sería nativo de Apple); (b) el backend
  `pytest` y los gates de CI del repo no cambian por un intent de capa de diseño;
  (c) el coste sigue siendo 0 € (sólo SDK de Apple); (d) el tema de Angular es la
  fuente de verdad y Google Stitch está descartado.

## Decisión: RE-RUN que REAFIRMA
Se reafirman las cinco secciones de `team.md` y los constraints duros de
`project.md` tal cual están, y se AÑADE exclusivamente el matiz nativo iOS en
`## Testing Posture` (portabilidad del arnés), `## Code Style` (fuente de verdad
del diseño + Stitch descartado) y `## Way of Working`/`## Deployment` (este
intent no toca CI/CD ni despliegue). No se introducen reglas nuevas no
establecidas.

## Incertidumbre que la entrevista debería resolver
- **Confirmar que es puramente reafirmación**: ¿el propietario acepta reafirmar
  el baseline sin cambios de práctica, con el único añadido del matiz SwiftUI?
- **Alcance del matiz de testing nativo**: ¿se registra como *riesgo documentado*
  (recomendación de este draft) o el equipo quiere ya comprometer un
  arnés/umbral de test de UI nativo (XCTest/snapshot) en este intent? El draft
  asume lo primero (sólo documentar), al ser un intent de diseño.
- **Nada más pendiente**: Way of Working, Walking Skeleton, Deployment y los
  constraints duros no requieren decisión nueva (son estado afirmado estable).
