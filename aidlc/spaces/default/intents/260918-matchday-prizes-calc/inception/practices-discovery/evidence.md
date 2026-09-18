# Evidencia — practices-discovery (260918-matchday-prizes-calc)

Re-run brownfield. Este documento registra qué se inspeccionó, qué se infirió y qué queda
incierto para que la **interview** lo resuelva antes de la afirmación.

## Fuentes inspeccionadas (rutas)

**Línea base afirmada (re-run):**
- `aidlc/spaces/default/memory/team.md` — 5 secciones afirmadas de intents previos.
- `aidlc/spaces/default/memory/project.md` — `## Mandated`/`## Forbidden`/`## Corrections`
  (coste 0 €, gate CI, characterization-first, JWT no-default, password no en claro).
- `aidlc/spaces/default/memory/org.md` — defaults del framework (trunk-based, squash).

**Reverse-engineering del área de premios (recién actualizado):**
- `codekb/futmondo-analytics/code-structure.md` — ubica la fórmula en
  `services/data_sync_service.py::sync_prizes` (~1577-1885), productor de `team_prizes`;
  endpoints solo leen/suman.
- `codekb/futmondo-analytics/code-quality-assessment.md` — GAP CRÍTICO: sin caracterización
  de la **producción** del premio; el **consumo** sí está caracterizado
  (`test_finance_characterization.py`). CI bloqueante = gitleaks+pytest+ng test.
- `codekb/futmondo-analytics/architecture.md` — flujo de premios en dos mitades desacopladas
  por `team_prizes` (escritura batch `sync_prizes` / lectura barata en routers).
- `codekb/futmondo-analytics/business-overview.md` — términos de negocio: points_prize
  (siempre), ranking_prize/mvp_prize/dream_team_prize (solo con ronda completa y cerrada).
- `codekb/futmondo-analytics/dependencies.md` — `sync_prizes` acopla API Futmondo (con
  `time.sleep()`) + BD; exige dobles/fakes para test a coste 0 €.

**Config real:**
- `.github/workflows/ci.yml` (PR→`main`): gitleaks + pytest (`--cov=app`) + ng test
  **BLOQUEANTES**; ruff/ESLint/pip-audit/npm audit **advisory** (`continue-on-error`).
- `.github/workflows/fly-deploy.yml` (push→`main`): job `verify` (gitleaks + pytest **sin
  `--cov`** + ng test) → deploy-backend → deploy-frontend → smoke `/health` (5 reintentos).
- `backend/pytest.ini`: `testpaths=tests`, `pythonpath=.`, corre desde `backend/`; cobertura
  informativa sin piso bloqueante.
- `backend/ruff.toml`: `select=["E","F","I"]`, `ignore=["E501","E402","E722"]`,
  `line-length=100`, `format` comillas dobles; advisory hoy.
- `angular-app/eslint.config.js` (flat config, advisory) y `.nvmrc` = `22.22.3`.
- Historial git: HEAD `ca0b151d` (merge PR #8 backend-security-hardening); commits en
  castellano con Conventional Commits y ramas `fix/…`, `chore/…`.

## Inferencias del lead

- La **Testing Posture** de línea base (test-after + characterization-first) aplica sin
  cambios de metodología; **solo se extiende el objetivo** de la caracterización de
  `SessionStore`/`TaskManager` a **`sync_prizes`** (producción del premio), que es el nuevo
  núcleo del intent y hoy tiene cobertura directa cero.
- El **Way of Working** no cambia (trunk-based, squash, MR con gate); el único matiz es la
  restricción brownfield: extraer la fórmula tras capa estrecha sin ampliar el god-file.
- El patrón de dobles a coste 0 € ya existe (`conftest.py`, `test_finance_characterization.py`
  con doble de `DataManagerV2`); es reutilizable para el fake de la API Futmondo.

## Incertidumbres para la interview

1. **Alcance del refactor de `sync_prizes`**: ¿el intent extrae la fórmula a una función/módulo
   estrecho testeable (recomendado por el RE) o se limita a corregir el cálculo *in situ* con
   solo la red de caracterización? Define cuánto "sin reescrituras grandes" se permite.
2. **Granularidad de la caracterización mínima**: ¿qué ramas de `sync_prizes` son de
   afirmación obligatoria antes de tocar (ranking flop/top, gating `round_fully_played`, MVP,
   dream-team, pseudo-jornada negativa, `DELETE ... NOT IN`)? ¿Todas, o un subconjunto crítico?
3. **Bugs conocidos a congelar vs corregir**: ¿hay comportamientos actuales de `sync_prizes`
   que el intent considere bug a corregir (y por tanto tests de fase 1 a retirar
   deliberadamente), o el objetivo es solo mejorar fiabilidad sin cambiar importes existentes?
4. **Cobertura**: ¿se mantiene la referencia global 80% líneas como no-bloqueante, o el equipo
   quiere activar un piso/ratchet para las piezas de premios en este intent?
5. **Paridad de `verify` con el gate de MR**: ¿se aborda en este intent que `verify`
   (push→`main`) corra `--cov` para no perder señal de cobertura, o queda diferido a diseño de
   pipeline?
6. **Doble semántica de "puntos"** (points como métrica vs `points_prize` monetario) y la
   **resolución de identidad frágil** en `player_finances`: ¿entran en el alcance del intent o
   se documentan como deuda fuera de alcance?

## Decisiones de la interview (autoritativas)

La interview (`practices-discovery-questions.md`) resolvió las seis incertidumbres. Son la
fuente de verdad y prevalecen sobre las inferencias del lead:

- **Q1 = A — Alcance del refactor**: el intent **EXTRAE la fórmula de premios a una
  función/módulo estrecho, puro y testeable** y corrige el cálculo ahí, **sin engordar** el
  god-file `data_sync_service.py`. Confirma la recomendación de quality y developer (extracción
  frente a corrección *in situ*).
- **Q2 = A — Caracterización obligatoria**: **TODAS las ramas de `sync_prizes` antes de tocar**:
  `points_prize`, gating `round_fully_played`, ranking flop/top, MVP, dream-team, jornada
  adelantada/negativa y el borrado defensivo `DELETE ... NOT IN`. devsecops reforzó que el
  `DELETE ... NOT IN` es la rama con potencial de pérdida de datos y debe caracterizarse sí o sí.
- **Q3 = C — Bugs a corregir**: **incertidumbre ABIERTA**. Aún no se sabe si hay bugs de cálculo
  a corregir; se decide en el análisis de **requisitos** y en la propia caracterización. Por
  tanto **NO se afirma que los importes cambien ni que se conserven**. Los tests de fase 1 que
  describan un comportamiento que luego se cambie a propósito se **retiran/actualizan de forma
  trazable**.
- **Q4 = A — Cobertura**: mantener **80% líneas como referencia global NO-bloqueante**; exigir
  solo tests para los **caminos nuevos y de error** de premios. Sin piso porcentual bloqueante
  adicional (evita ruido brownfield, avalado por quality).
- **Q5 = A — Paridad `verify`↔gate-de-MR**: **DIFERIR** a un futuro diseño de pipeline la paridad
  de `--cov` en `verify` (push→`main`); fuera de alcance de este intent. Aclaración de devsecops:
  la **paridad de SEGURIDAD (gitleaks) ya está cerrada** en ambos caminos; **lo único diferido es
  la señal de cobertura `--cov`**, decisión de calidad/pipeline, no de seguridad.
- **Q6 = A — Deuda adyacente**: la **doble semántica de "puntos"** y la **resolución de identidad
  por nombre** en `player_finances` quedan **FUERA de alcance**: se documentan como deuda conocida
  y **no se tocan**. Recomendación aditiva de developer conservada: el código NUEVO debe usar
  naming desambiguador (`*_points` métrica vs `*_prize`/`*_amount` dinero).

### Incertidumbre que permanece abierta tras la interview

- **Q3 (bugs de cálculo)**: es la única incertidumbre que la interview deja **deliberadamente
  abierta**, delegada al **análisis de requisitos** y a la caracterización. Hasta entonces, la
  postura de test no presupone cambio ni conservación de importes; se congela el comportamiento
  actual y se decide después, de forma trazable. Las demás incertidumbres (Q1, Q2, Q4, Q5, Q6)
  quedan cerradas por las respuestas anteriores.
