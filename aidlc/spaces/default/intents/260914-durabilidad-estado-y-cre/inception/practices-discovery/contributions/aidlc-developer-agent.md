**Collaborator:** aidlc-developer-agent

## Contribution

Revisión independiente del borrador del lead (proyecto brownfield `futmondo-analytics`),
centrada en las cinco áreas encargadas: nombrado, límites de capas, manejo de errores,
organización de ficheros y convenciones de estilo. Verifiqué el borrador contra el código
real de `backend/app/` (auth, services, api) además de la CodeKB.

En conjunto, el borrador es sólido y bien anclado en evidencia. Confirmo las prácticas
centrales (trunk-based, test-after + characterization-first, coste 0 €, estilo escalonado
advisory→bloqueante, sin walking skeleton). A continuación, precisiones y hallazgos
adicionales que la evidencia de código respalda y que el borrador no cubre o describe de
forma inexacta.

### Nombrado (confirmado, con una corrección)

- **AGREE en lo esencial**: el nombrado del backend es idiomático y consistente. Funciones
  verbo+sustantivo (`create_access_token`, `revoke_all_user_tokens`, `get_user_futmondo_client`),
  booleanos con prefijo (`is_expired`, `is_authenticated`, `is_refresh_token_valid`),
  clases-sustantivo (`SessionStore`, `TaskManager`, `UserSession`, `DBConnection`),
  constantes SCREAMING_SNAKE_CASE (`SESSION_TTL`, `ACCESS_TOKEN_EXPIRE_MINUTES`,
  `REFRESH_COOKIE_MAX_AGE`). snake_case en Python es uniforme.
- **Corrección al draft (`## Code Style`, "castellano en prosa, mensajes de commit y
  comentarios")**: en el código verificado, docstrings y comentarios están **en inglés**
  (`session_store.py`, `token_store.py`, `db_connection.py`, `routes.py`, `_helpers.py`,
  `jwt_utils.py`, `dependencies.py`). Lo que está en castellano son los `detail` de
  `HTTPException` de cara al usuario y la prosa de commits/documentación. La convención real
  observable es: **identificadores y comentarios en inglés; texto de cara al usuario en
  castellano**. Conviene afirmarla así de forma explícita para no inducir a escribir código o
  comentarios nuevos en castellano.

### Límites de capas (hallazgo relevante para el intent, no cubierto por el draft)

El estilo declarado es "router-per-domain + clientes de integración dedicados", pero el
código muestra **fuga de la capa de acceso a datos hacia arriba**, directamente en el área
que este intent va a tocar:

- `app/auth/token_store.py` (capa auth) contiene DDL y SQL directo, incluyendo la tabla de
  dominio `user_championships` (no es un token) — mezcla identidad, tokens y configuración de
  dominio en un mismo módulo.
- `app/auth/routes.py::_auto_detect_championships` es un handler de ~150 líneas que abre
  conexiones, arma SQL crudo con ramas por dialecto, y hace `INSERT`/`UPDATE` sobre
  `user_championships` en línea. El router habla SQL directamente, sin capa repositorio.
- `app/api/v1/endpoints/_helpers.py::get_championship_config` repite el mismo patrón
  (endpoint → SQL crudo).

No hay una capa repositorio/DAO: el SQL se reparte entre auth, endpoints y `services/`.
Para un intent de **durabilidad de estado** esto importa: si el estado durable de
`SessionStore`/`TaskManager` se implementa replicando este patrón (SQL crudo esparcido con
ramas `if db.db_type in [...]`), la deuda de acoplamiento crece. **Recomiendo afirmar como
práctica**: introducir/usar una capa de persistencia estrecha (funciones tipo repositorio en
`services/` o un módulo `stores/` dedicado) para el nuevo estado durable, en lugar de SQL en
routers. Al menos, no ampliar el patrón actual de SQL-en-router.

### Manejo de errores (hallazgos que contradicen guardrails vigentes)

`org.md`, `phases/inception.md` y `phases/construction.md` exigen "nunca tragar excepciones
en silencio" y manejo explícito en fronteras. El código tiene infracciones concretas y
verificadas:

- **Bug de precedencia confirmado** en `token_store.is_refresh_token_valid` (línea del
  chequeo de expiración): la comparación usa una ternaria sin paréntesis
  (`... > expires_at.replace(...) if expires_at.tzinfo is None else expires_at`), cuya
  precedencia hace que la rama `else` devuelva el propio `expires_at` (truthy) en vez de una
  comparación booleana. Es un posible fallo de validación de expiración de refresh tokens
  (seguridad). El draft de `architecture.md` ya lo señala como "posible bug"; desde código
  lo confirmo como real y **recomiendo caracterizarlo con un test antes de tocar auth** en
  este intent (encaja con characterization-first).
- **`except Exception: pass` silenciosos**: en `token_store.init_auth_tables` (migraciones
  `ALTER TABLE`) y en `routes._auto_detect_championships` (lookup de `existing_config`). El
  patrón `except ...: pass` asumiendo "la columna ya existe" enmascara cualquier otro error
  de BD.
- **Captura ancha con solo log**: varios `except Exception as e: logger.warning/debug` en
  `routes.py` (auto-detección) — aceptable como frontera de endpoint, pero conviene
  distinguir errores esperados de fallos reales.
- **`db_connection.get_connection`** tiene varios `except Exception: pass` en el reciclado
  del pool; es defendible como resiliencia, pero merece al menos log de diagnóstico.

**Recomiendo afirmar**: el estado durable nuevo (FR1) debe manejar errores de I/O de BD de
forma explícita (no `except: pass`), fallar ruidoso en el arranque/escritura crítica y no
degradar silenciosamente. Esto es alineación con los guardrails de fase, no una regla nueva.

### Organización de ficheros (god-files, relevante para sync)

El estilo declara "deferir a config del proyecto", pero no captura una desviación fuerte de
la guía de código: `app/services/data_manager_v2.py` (**166 KB**) y `data_sync_service.py`
(**84 KB**) son ficheros-dios muy por encima de cualquier umbral razonable de tamaño/
responsabilidad. Como el intent toca `TaskManager`/sync, la ruta de `data_sync_service` es
vecina directa. **Recomiendo** una nota de práctica brownfield: no ampliar estos módulos con
la lógica de durabilidad; ubicar el nuevo estado durable en módulos nuevos y acotados. No
propongo refactor de los god-files existentes (fuera de alcance y riesgo alto sin cobertura).

### Convenciones de estilo (confirmado, con dos matices)

- **AGREE** con ruff (`E,F,I`, ignore `E501/E402/E722`, `line-length=100`, py312, comillas
  dobles) advisory hoy, ESLint flat-config advisory, prettier, Node `.nvmrc=22.22.3`.
- **Matiz 1 — imports diferidos**: el draft normaliza los imports dentro de funciones como
  "tolerados (E402 ignorado)". Ojo: `E402` es *module-level import not at top*, no *import
  dentro de función*; los imports diferidos (p. ej. `from app.services.db_connection import
  get_db` dentro de funciones en `token_store`, `_helpers`, `routes`) no los cubre E402. Son
  una convención de facto para evitar ciclos, no algo que el linter esté silenciando. Y el
  caso extremo `__import__('app.services.db_connection', ...)` dentro de `refresh` es un
  antipatrón de legibilidad (el propio módulo ya importa `get_db` estáticamente en otras
  funciones). **Recomiendo** afirmar "preferir import estático a nivel de módulo salvo ciclo
  demostrable; prohibir `__import__` dinámico".
- **Matiz 2 — placeholders SQL**: la adaptación manual `?`↔`%s` vía `db.adapt_params` +
  ramas `if db.db_type in ["postgresql","postgres"]` está repetida por todo el código
  (auth, endpoints). Es frágil y propensa a errores al añadir estado durable. No es
  bloqueante para practices, pero conviene registrarlo como riesgo de estilo/consistencia.

### Sobre estrategia de merge (apoyo al punto abierto del lead)

Confirmo que el punto que el lead deja para entrevista (merge commit de PR #1 vs squash-merge
por defecto de `org.md`) es un conflicto real de evidencia y **debe resolverlo el humano**;
no lo afirmo en ninguna dirección desde código.

## Positions

AGREE: Trunk-based sobre `main`; base/destino `main`; sin walking skeleton para este
brownfield acotado (`skeleton: off`).
AGREE: Testing Posture `Methodology: test-after`, `Ordering` characterization-first en
brownfield, suite existente en verde; sin piso de cobertura bloqueante hoy.
AGREE: Deploy on-merge a Fly.io (`cdg`) sin staging, smoke test `/health`; crons one-shot;
coste 0 €.
AGREE: Estilo escalonado advisory→bloqueante (ruff/ESLint advisory, gitleaks/pytest/ng test
bloqueantes); deferir a linter/formatter del proyecto; Node `.nvmrc`.
AGREE: Reglas `Mandated`/`Forbidden` sobre coste 0 €, characterization-first de
`SessionStore`/`TaskManager`, gate de CI bloqueante, `JWT_SECRET` no-default, no credenciales
en claro, no servicios de pago.

OBJECT: `## Code Style` afirma "castellano en ... comentarios". El código real tiene
docstrings/comentarios **en inglés**; solo el texto de cara al usuario (`detail`) y la prosa
de commits/docs están en castellano. Corregir a: "identificadores y comentarios en inglés;
texto de cara al usuario en castellano".

OBJECT: El borrador no captura la **ausencia de capa de persistencia** (SQL crudo en auth y
en routers, DDL de dominio dentro de `auth/token_store.py`). Para un intent de durabilidad,
añadir una práctica: el nuevo estado durable se implementa tras una capa repositorio/store
estrecha, sin ampliar el patrón de SQL-en-router.

OBJECT: El borrador no eleva el **manejo de errores** como práctica pese a las infracciones
verificadas (`except Exception: pass` en migraciones y auto-detección; bug de precedencia en
`is_refresh_token_valid`; `__import__` dinámico en `refresh`). Añadir: el estado durable
nuevo debe manejar errores de I/O de BD de forma explícita y ruidosa (alineado con guardrails
de fase), y caracterizar el bug de expiración de refresh antes de refactorizar auth.

OBJECT (menor): El borrador no menciona los **god-files** `data_manager_v2.py` (166 KB) y
`data_sync_service.py` (84 KB). Añadir nota brownfield: la durabilidad no debe ampliarlos;
ubicar el estado durable en módulos nuevos y acotados.
