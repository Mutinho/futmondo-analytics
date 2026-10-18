**Collaborator:** aidlc-quality-agent

## Contribution

Revisión de calidad del borrador del lead (ciega al resto de agentes de apoyo),
centrada en la posture de testing, el tooling de cobertura, los gates de CI y los
huecos que debe resolver la entrevista humana. El veredicto global: el borrador
**acierta** al tratar la posture test-after y el principio «el trinquete sólo
sube» como **línea base durable** y al **excluir** del alcance de ESTE intent los
pisos de cobertura concretos, la paridad de señal y la promoción escalonada de
linters/audits (trabajo propio de los intents de CI gate-hardening). Para un
intent cuyos entregables son **documentos de análisis**, no hay capa de software
testeable nueva, así que la única obligación operativa de testing es correcta:
**la suite existente sigue en verde**. Aun así hay matices y un hueco de calidad
que conviene integrar.

### 1. La posture test-after y el trinquete están bien portados — con una precisión

- El borrador recoge test-after como metodología durable y el trinquete como
  invariante («sólo sube; el flapping se arregla en el test no-determinista, no
  bajando el piso»). Correcto y fiel a `team.md`.
- Precisión sobre la obligación «suite en verde»: un intent de **análisis** no
  modifica código de aplicación, así que **no debería** disparar fallos de la
  suite backend/frontend. Pero el gate de CI (`ci.yml` → job `quality`) corre de
  todas formas en el PR documental, y dentro de `ng test` el enforcement de
  cobertura es **bloqueante** (`coverageThresholds` en `angular.json`): si el
  entorno de CI mide cobertura de forma no-determinista, un PR puramente
  documental podría ponerse rojo por flapping ajeno al cambio. Conviene que la
  línea base diga explícitamente que, ante ese caso, se **arregla el test
  no-determinista** (nunca se baja el umbral ni se añade `continue-on-error`),
  coherente con el invariante del trinquete.

### 2. Hueco de calidad propio del intent de viabilidad: la **estrategia de test del target nativo**

Éste es el hallazgo más relevante y hoy **no aparece** en el borrador. Un
análisis de viabilidad de Angular Native debe evaluar la **portabilidad de la
posture de testing**, no sólo la de la UI:

- **Frontend**: la suite actual son **15** `*.spec.ts` sobre `@angular/build:unit-test`
  (builder Vitest `4.1.11` + `@vitest/coverage-v8` + `jsdom`). En NativeScript ese
  builder **no existe**: no hay DOM/`jsdom`, el runner Angular CLI de Vitest no
  aplica, y los tests que montan componentes Material/CDK (DOM) **no portan**. La
  feasibility debe señalar que migrar a nativo implica **rehacer el arnés de test
  de frontend** (p. ej. `@nativescript/unit-test-runner` + Karma/Jasmine o
  Mocha), que los specs de **servicios/RxJS/signals** son portables casi 1:1 pero
  los de **componentes de vista** no, y que el umbral de cobertura frontend
  tendría que **re-basarse** sobre el nuevo runner (no es un trinquete que suba:
  es un suelo nuevo bajo tooling distinto). Esto es un riesgo de calidad de
  primer orden que condiciona la ruta de implementación.
- **Backend**: **sin cambios** — la migración de UI nativa no toca `pytest` ni el
  piso `--cov-fail-under=27`; conviene decirlo explícitamente para que nadie
  induzca trabajo de testing backend inexistente.
- **E2E / dispositivo**: el salto a nativo introduce una dimensión de test que
  hoy no existe (prueba en iPhone 13 Pro / Samsung A17, build Xcode / Android
  SDK). La feasibility debería al menos **nombrar** esa necesidad (device/E2E
  testing, posiblemente Detour/Appium o Playwright-mobile) y su coste/herramienta,
  aunque la decisión concreta sea de stages posteriores.

### 3. Cifras de cobertura: usar las MEDIDAS, no las de memoria

El borrador cita backend `--cov-fail-under=27` y frontend statements 19 /
branches 19 / functions 17 / lines 18 como «estado heredado que este intent no
modifica». Correcto, y bien marcado como «No aplica en este intent». Una nota de
calidad: `code-quality-assessment.md` deja claro que las cifras de god-files en
`project.md` están **desactualizadas** (p. ej. `data_manager_v2.py` «~166 KB» →
33 KB real; `assistant_service.py` «~51 KB» → 2,3 KB shim). Como la feasibility
razonará sobre el esfuerzo de portar/rehacer código, debe apoyarse en las cifras
**medidas en el scan**, no en las de memoria, para no sobredimensionar el riesgo.

### 4. Confirmación de que el gate está bien enumerado

La lista de pasos del gate en el borrador (`gitleaks + ruff check + pytest +
pip-audit + ng test + npm audit`) coincide **exactamente** con `ci.yml` (job
`quality`) y con el job `verify` de `fly-deploy.yml`. ESLint frontend sigue
**advisory** (`continue-on-error: true`, devDependencies no instaladas), bien
reflejado como deuda diferida. Nada que corregir aquí.

### 5. Huecos para la entrevista humana (calidad)

- ¿La estrategia de test del target nativo (runner de frontend, cobertura
  re-basada, E2E en dispositivo) debe entrar como **sección de la feasibility** o
  se difiere a un stage posterior? (Recomendación de calidad: nombrarla como
  riesgo en feasibility.)
- ¿Alguno de los invariantes de CI gate-hardening (allowlist versionada con
  caducidad, pin de tooling del gate) se eleva ahora a **durable de equipo** y
  debe quedar en `team.md` aunque este intent no lo ejercite? (Ya listado como
  Open Question #1 del lead; lo respaldo desde calidad.)

## Positions

AGREE: La posture test-after y el trinquete «sólo sube» están correctamente
tratados como línea base durable y bien excluidos del alcance de un intent de
análisis.

AGREE: La única obligación operativa de testing («suite existente en verde») es
la adecuada para un intent que sólo entrega documentos.

AGREE: Excluir pisos de cobertura concretos, paridad de señal y promoción
advisory→bloqueante (trabajo de intents CI gate-hardening) es correcto.

OBJECT: Falta un hueco de calidad propio del intent: la **feasibility no evalúa
la portabilidad de la posture de testing** (el builder Vitest/`jsdom` del
frontend no existe en NativeScript → arnés de test de UI a rehacer, cobertura
frontend a re-basar, E2E/device testing nuevo). Debe señalarse como riesgo.

OBJECT: La nota «suite en verde» debería blindar explícitamente que un rojo por
flapping de cobertura en un PR documental se resuelve arreglando el test
no-determinista, **nunca** bajando el umbral ni añadiendo `continue-on-error`
(coherencia con el invariante del trinquete).
