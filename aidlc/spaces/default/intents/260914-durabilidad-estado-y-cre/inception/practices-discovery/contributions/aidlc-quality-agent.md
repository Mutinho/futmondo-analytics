**Collaborator:** aidlc-quality-agent

## Contribution

Revisión independiente del borrador del lead centrada en calidad: postura de testing,
herramientas de cobertura, gates de CI, patrones de test/código y los huecos que la
entrevista humana debe cerrar. Verifiqué la evidencia sobre el repositorio real
(`backend/pytest.ini`, `backend/conftest.py`, `backend/tests/`, `.github/workflows/ci.yml`,
`.github/workflows/fly-deploy.yml`, `angular-app/angular.json`) y el CodeKB
(`code-quality-assessment.md`). El borrador es sólido y está bien anclado en evidencia;
aporto precisiones y refuerzos integrables.

### Postura de testing (methodology + ordering)

- **Methodology = test-after** y **Ordering** characterization-first en brownfield están
  bien resueltos y coinciden con `org.md` (default test-after) y con la evidencia
  (`conftest.py` declara explícitamente "congelar el comportamiento ACTUAL antes de
  refactorizarlo"). AGREE.
- Refuerzo integrable para la sección `## Testing Posture`: hacer explícito el **orden de
  dos fases** para este intent, porque es la garantía de calidad del refactor de estado:
  1. **Fase caracterización (antes de tocar `SessionStore`/`TaskManager`)**: escribir
     tests que congelen el comportamiento observable actual, *incluido el comportamiento
     de fallo* — reinicio pierde sesión (`_helpers` → 403), tarea de sync huérfana tras
     redeploy. Estos tests deben pasar contra el código actual (rojo→verde no aplica: es
     red de seguridad, no TDD).
  2. **Fase durabilidad (test-after)**: implementar la persistencia y después escribir
     los tests del *nuevo* contrato (sesión reconstruida tras reinicio, idempotencia de
     tarea, no reintroducir `password` en claro). Al terminar, los tests de
     caracterización de la fase 1 que describían el *fallo* se **actualizan/retiran**
     de forma deliberada y trazable (no se borran en silencio), porque el comportamiento
     esperado cambió a propósito.
- **Definición mínima de "hecho" (testing) para el intent**, integrable como criterio de
  gate del propio trabajo: `SessionStore` y `TaskManager` pasan de 0 tests a cubiertos en
  caracterización *antes* del refactor, y con tests del nuevo contrato de durabilidad
  *después*. Sin esa red, el refactor del núcleo del intent no debería fusionarse.

### Herramientas de cobertura

- Confirmo: `pytest` + `pytest-cov` en backend (invocable con `--cov=app`), Vitest+jsdom
  en frontend vía `@angular/build:unit-test`. AGREE con el inventario del lead.
- **Precisión verificada**: no existe **ningún** piso de cobertura en el repo — busqué
  `cov-fail-under` / `fail_under` / `coverageThreshold` / `--coverage` y no hay
  coincidencias. La cobertura es hoy 100% informativa, tal como dice el lead. Sugiero que
  la sección lo enuncie como decisión consciente ("cobertura como métrica, ratcheting
  diferido") y no como omisión, para que la entrevista decida si activar un floor
  *diferencial* (líneas nuevas/tocadas) — más barato de sostener en un frontend con un
  único spec real que un floor global 80%, que hoy fallaría de inmediato.
- **Matiz de coste 0 €**: cualquier gate de cobertura debe correr dentro de GitHub Actions
  free (ya lo hace `pytest --cov`); no requiere servicio de pago. Sin fricción con la
  restricción de coste.

### Gates de calidad en CI

- Confirmo el gate escalonado: gitleaks + `pytest` (con `--cov`) + `ng test` **bloqueantes**;
  ruff/ESLint/pip-audit/npm audit **advisory** (`continue-on-error: true`). AGREE con la
  descripción del lead.
- **Divergencia que el borrador NO recoge y debería** (hueco de calidad real): el job
  `verify` de `fly-deploy.yml` (push→`main`) **no es idéntico** al gate de PR:
  - corre `pytest -q` **sin `--cov`** (no recolecta cobertura en el camino de deploy), y
  - **no ejecuta gitleaks** en el re-verify.
  Es defensa en profundidad razonable (el PR ya gateó), pero la asimetría importa para un
  push directo a `main` (que `org.md` permite re-verificar): un secreto introducido en un
  push directo *no* lo detendría el re-verify, solo el gate de PR. Propongo que la sección
  `## Testing Posture`/`## Deployment` anote esta asimetría y que la entrevista decida si
  se acepta (confiando en branch protection para forzar PRs) o si `verify` debe replicar
  gitleaks. Esto es directamente relevante a FR5 (credenciales) y al objetivo del intent.

### Patrones de test/código

- **Patrón de aislamiento sólido y reutilizable**: `conftest.py` inyecta fakes de
  `DataManager`/conexión y factories para APIs externas, y la fixture `clean_jwt_env`
  aísla variables de entorno de arranque. El diseño de durabilidad debe seguir el mismo
  patrón: **fakes de la capa de persistencia** (repo/almacén en memoria para el test) en
  lugar de BD Neon real, para que los tests sigan siendo rápidos, deterministas y sin
  coste. Integrable como nota de patrón en `## Code Style`/`## Testing Posture`.
- **Independencia de tests**: la fixture actual limpia entorno por test; al persistir
  estado, cada test debe crear y limpiar su propio almacén (o usar transacción con
  rollback / almacén en memoria) — nunca compartir estado mutable entre tests. Es
  especialmente crítico aquí porque el sujeto bajo prueba *es* estado compartido de
  proceso hoy.
- **Anti-patrón a vigilar en el nuevo código**: el CodeKB señala varios
  `except Exception: pass` (migraciones, auto-detección). El guardrail de fase
  (`construction.md`: "silent failures are not acceptable") aplica: los tests del nuevo
  contrato de durabilidad deben **forzar y afirmar** el camino de error (fallo de
  persistencia, reconexión), no dejarlo tragado. Integrable como criterio de test.

### Huecos que debe resolver la entrevista humana (desde calidad)

1. **¿Se activa un piso de cobertura y de qué tipo?** Recomiendo diferencial (líneas
   nuevas del intent) sobre `SessionStore`/`TaskManager`; decidir umbral concreto.
2. **Asimetría del gate de deploy**: ¿`verify` de `fly-deploy.yml` debe replicar gitleaks
   y `--cov`, o se delega íntegramente a branch protection + gate de PR?
3. **Estrategia de test de durabilidad**: ¿fake en memoria de la capa de persistencia
   (rápido, coste 0) o test de integración contra una BD Neon efímera/local? Impacta
   tiempo de CI y coste.
4. **Qué se considera "reinicio" en test**: cómo simular el redeploy Fly (`min=max=1`)
   para probar reconstrucción de sesión y idempotencia de tarea sin instancia real.
5. **Volumen de test**: confirmar el eje `Test Strategy` activo del intent (Minimal vs
   Standard) — el lead correctamente lo delega a ese eje; falta fijar el valor.
6. **Divergencia comentario↔comportamiento** (`_helpers.get_user_futmondo_client` promete
   reconstruir sesión pero da 403): ¿se cubre con un test de caracterización que congele
   el 403 actual antes de corregirlo en la fase de durabilidad? Recomiendo que sí.

## Positions

- AGREE: `Methodology: test-after` con ordering characterization-first — coincide con `org.md` y con la declaración explícita de `backend/conftest.py`.
- AGREE: cobertura informativa sin piso bloqueante hoy — verificado, no existe `cov-fail-under`/`fail_under`/`coverageThreshold` en el repo.
- AGREE: gate de PR con gitleaks+`pytest`+`ng test` bloqueantes y lint/audit advisory — confirmado en `.github/workflows/ci.yml`.
- AGREE: hueco crítico "no hay tests de `SessionStore`/`TaskManager`" y su obligatoriedad antes de refactorizar — es el riesgo de calidad central del intent.
- OBJECT: el borrador describe el re-verify de deploy como equivalente al gate, pero `verify` en `fly-deploy.yml` corre `pytest` sin `--cov` y sin gitleaks — la asimetría debe anotarse y resolverse en la entrevista (relevante a FR5).
- OBJECT: falta enunciar la cobertura como decisión consciente con opción de floor diferencial sobre el núcleo del intent; dejarlo solo como "sin piso" arriesga que el refactor del estado se fusione con cero cobertura verificable.
