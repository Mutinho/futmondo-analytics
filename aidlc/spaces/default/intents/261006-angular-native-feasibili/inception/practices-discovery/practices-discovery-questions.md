# Practices Discovery — Preguntas de la entrevista

Re-run brownfield para un intent de **análisis de viabilidad** (Angular Native). La línea
base durable de prácticas (coste 0 €, gate de CI bloqueante, trunk-based + squash-merge,
test-after, deploy on-merge a Fly.io, identificadores en inglés / texto de usuario y commits
en castellano, no secretos en claro) ya está afirmada y se arrastra sin cambios. Sólo se
pregunta lo que el borrador y las revisiones no pudieron establecer.

## Q1 — Coste de la cuenta de desarrollador Apple vs mandato de coste 0 €

Publicar/firmar una app iOS nativa exige una cuenta de Apple Developer (~99 €/año), lo que
choca con la regla dura de "coste 0 €, sólo tiers gratuitos". Para el análisis de viabilidad,
¿cómo tratamos ese coste?

- A. Factor **excluyente**: si exige salir de coste 0 €, el análisis debe concluir no-viable salvo alternativa gratuita.
- B. **Excepción aceptable y acotada**: el coste de publicación nativa (Apple/Google) es una excepción conocida al mandato de coste 0 €; el análisis sigue adelante y lo documenta como coste recurrente de distribución.
- C. Analizar **ambos escenarios** (con y sin cuenta de pago) y dejar la decisión para la fase de implementación.
- X. Other (please specify)

[Answer]: B

## Q2 — ¿Elevar alguna regla de CI gate-hardening a regla durable de equipo?

Varias reglas afirmadas en intents previos son específicas de aquel trabajo de CI
(pisos de cobertura concretos, promoción advisory→bloqueante, allowlist versionada con
caducidad, pin de tooling del gate). El escaneo de dependencias (`pip-audit`/`npm audit`) y de
secretos (`gitleaks`) **ya es bloqueante** en ambos gates. ¿Quieres que alguna de estas suba a
regla **durable de equipo** (quedando en `team.md`/`project.md` aunque este intent no la ejercite)?

- A. **No**: mantener la línea base durable tal cual; esas reglas son estado del repo e historia de intents previos, no reglas de equipo nuevas.
- B. **Sí**: elevar el **escaneo de dependencias y secretos bloqueante** a control de cadena de suministro durable (separándolo de la mecánica intent-específica de promoción/allowlist/pin).
- C. Sí, elevar alguna otra regla concreta — la indico en "Other".
- X. Other (please specify)

[Answer]: B

## Q3 — Alcance de los riesgos técnicos nativos (testing + secure storage) en este intent

Las revisiones señalaron riesgos técnicos de la migración nativa: (a) el arnés de test de UI
se rehace (NativeScript no tiene el builder Vitest/jsdom actual; aparece dimensión E2E/device),
y (b) el refresh token debe ir a almacenamiento seguro nativo (iOS Keychain / Android Keystore),
no en claro. ¿Dónde quieres que vivan estos riesgos?

- A. **Dentro de este análisis de viabilidad**: tratarlos como secciones/riesgos del propio informe de feasibility.
- B. **Diferidos**: anotarlos como entradas de reenvío a stages posteriores (p. ej. diseño), fuera del alcance del análisis actual.
- C. Mezcla: el riesgo de **sesión/secure storage** entra en el análisis (es central a la viabilidad); el **detalle de testing** se difiere.
- X. Other (please specify)

[Answer]: C

## Consolidated Summary Confirmation

Does this all look correct before I generate the artifact?

[Answer]: Looks correct
