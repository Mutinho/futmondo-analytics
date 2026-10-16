**Collaborator:** aidlc-devsecops-agent

## Contribution

Revisión de seguridad y cadena de suministro del borrador lead, independiente y a ciegas respecto al resto de agentes de apoyo. El intent `261006-angular-native-feasibili` (scope `classic`) es un **análisis de viabilidad** de migrar a Angular Native (NativeScript + Angular): los entregables son documentos, no código de aplicación ni cambios de CI/CD. La revisión evalúa (1) si las reglas de seguridad **durables** están correctamente capturadas, (2) si las reglas **intent-específicas** de CI gate-hardening están correctamente NO arrastradas, y (3) qué consideraciones de seguridad NUEVAS debe señalar el análisis de migración nativa.

### Reglas de seguridad durables — correctamente capturadas

- **No hardcodear secretos/tokens reales** (`discovered-rules.md` → `## Forbidden`): correcto y bien ampliado al árbol de documentos de análisis («código, specs, workflows ni documentos de análisis»). Alineado con el estado real del repo: `gitleaks/gitleaks-action@v3` corre **BLOQUEANTE** en AMBOS gates (`ci.yml` job `quality` y `fly-deploy.yml` job `verify`), con `fetch-depth: 0` para escanear el historial del PR. La regla es durable, no intent-específica. **AGREE.**
- **Gate de CI bloqueante antes de fusionar a `main`, también para cambios documentales** (`## Mandated`): correcto. El job `verify` de `fly-deploy.yml` replica el gate en push directo porque `needs:` no cruza workflows (defensa en profundidad FR8.2/NFR2.1), de modo que un rojo —incluido un secreto detectado por gitleaks— nunca llega a producción. Que aplique «también para cambios puramente documentales» es la lectura correcta para un intent que sólo produce prosa.
- **Coste 0 € con dependencias OSS fijadas a versión exacta** (`## Mandated` + `## Forbidden`): correcto y relevante a seguridad de cadena de suministro (pin reproducible evita que un tooling flotante introduzca reglas/CVEs no deterministas). El borrador señala con acierto que **cualquier librería propuesta en la ruta de implementación sería OSS y fijada a versión exacta**, sin comprometer pins concretos en un intent de análisis.
- **No almacenar la contraseña Futmondo en claro** (`## Forbidden`): correctamente capturada Y correctamente conectada al riesgo de portabilidad del modelo de sesión nativo. Es la regla de seguridad con mayor relevancia para este análisis (ver abajo).

### Reglas intent-específicas — correctamente NO arrastradas

Confirmo que el lead acierta al **no** arrastrar como reglas de equipo las de los intents de CI gate-hardening (FR11/FR12/FR17.3): promoción escalonada advisory→bloqueante, **allowlist versionada con caducidad** (`backend/.pip-audit-allowlist` + `scripts/check-allowlist-expiry.sh`), pin de `ruff==0.16.9` / `pip-audit==2.10.1` / `vitest` al step que los instala, y pisos de cobertura concretos. Estas son **mecánica de un intent que tocaba `ci.yml`/`fly-deploy.yml`**; este intent no toca CI, así que son estado heredado del repo, no obligaciones de equipo re-afirmables aquí.

Matiz de precisión (no bloqueante): `pip-audit` y `npm audit --audit-level=high` **ya son bloqueantes en producción** hoy (los leo verbatim en ambos workflows); lo que NO se arrastra es el *trabajo* de promoverlos ni la mecánica de allowlist/pin, no el hecho de que el escaneo de dependencias exista. El borrador lo trata correctamente como «no aplica en este intent» en `team-practices.md`; sugiero que la integración final deje claro que **el escaneo de dependencias es parte de la línea base durable del gate** (es, al fin y al cabo, un control de cadena de suministro permanente), separándolo de las reglas de promoción que sí son intent-específicas.

### Consideraciones de seguridad NUEVAS que el análisis de migración debe señalar

El análisis de viabilidad debe tratar estos puntos como **riesgos a documentar**, no como decisiones a cerrar aquí:

1. **Portabilidad del modelo de sesión — riesgo de seguridad #1.** El modelo actual (access token en memoria + refresh token en cookie `HttpOnly` con `withCredentials`) **no existe igual en nativo**: no hay cookie `HttpOnly` del navegador. Mover el refresh token a **almacenamiento seguro nativo** (iOS Keychain / Android Keystore vía `@nativescript/secure-storage`, no `ApplicationSettings` en claro ni los **17 usos de `localStorage`** actuales) es obligatorio para preservar la garantía durable de no-credenciales-en-claro. STRIDE: Information Disclosure + Spoofing (robo de token en reposo). El análisis debe señalar que `ApplicationSettings` NO es almacenamiento cifrado y no sirve para el refresh token.
2. **Pérdida del aislamiento de JS que da `HttpOnly`.** En web la cookie `HttpOnly` es inaccesible a JS; en nativo el token vive en código accesible al runtime de la app → el modelo de amenaza cambia (app comprometida / dispositivo rooteado-jailbroken). Documentar como riesgo, con mitigación = almacenamiento respaldado por hardware + binding al dispositivo.
3. **Distribución nativa amplía la superficie de cadena de suministro.** `gitleaks` + `pip-audit` + `npm audit` cubren hoy Python/npm, pero una app NativeScript añade plugins nativos (CocoaPods/Gradle) que **ningún escáner actual del gate cubre**. El análisis debe señalar que una futura migración necesitaría extender el escaneo de dependencias a las dependencias nativas (coste 0 € con herramientas OSS), sin comprometer la herramienta concreta aquí.
4. **Build/firma nativa y coste.** La restricción coste 0 € puede tensionarse: Apple Developer Program (~99 €/año) y firma de código. Correctamente ya señalado por el lead como pregunta abierta; desde seguridad, añadir que la **firma de artefactos** (integridad de la build) es un control deseable, no sólo un coste.
5. **`curl_cffi` (impersonación de navegador contra Sofascore).** Dependencia backend sensible por su naturaleza de evasión de bloqueos; aunque el backend no cambia en una migración nativa de UI, conviene que el análisis anote que el pin exacto y el escaneo de esta dependencia deben mantenerse (riesgo de supply-chain de una lib de nicho).

Ninguna de estas consideraciones altera las reglas durables de `discovered-rules.md`; son insumos para los documentos de feasibility y para stages posteriores (domain-design / contract-design), no reglas de equipo a afirmar en esta etapa.

## Positions

AGREE: Las reglas durables de seguridad (no secretos hardcodeados, gitleaks bloqueante en ambos gates, OSS pinned/coste 0 €, no password Futmondo en claro) están correctamente capturadas y bien ampliadas al árbol de documentos.
AGREE: Las reglas intent-específicas de CI gate-hardening (allowlist con caducidad, pins concretos, promoción escalonada, pisos de cobertura) están correctamente NO arrastradas para un intent de análisis.
AGREE: Conectar la regla «no password Futmondo en claro» con el riesgo de portabilidad del modelo de sesión nativo es la decisión de seguridad más acertada del borrador.
OBJECT: `discovered-rules.md`/`team-practices.md` deberían distinguir que el **escaneo de dependencias (pip-audit/npm audit) es un control de cadena de suministro durable del gate**, separándolo de la *mecánica* de promoción/allowlist/pin que sí es intent-específica — tal como está redactado puede leerse como que el escaneo de dependencias no es parte de la línea base.
OBJECT: Falta en los durables una nota (aunque sea de reenvío a feasibility) de que el refresh token debe ir a **almacenamiento seguro nativo** y nunca a `ApplicationSettings`/`localStorage` en claro, para que la garantía de no-credenciales-en-claro no se pierda al perder la cookie `HttpOnly`.
