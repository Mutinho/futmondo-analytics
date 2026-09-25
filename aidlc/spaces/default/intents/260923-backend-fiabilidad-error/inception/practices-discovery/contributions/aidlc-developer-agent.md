**Collaborator:** aidlc-developer-agent

## Contribution

Reviso el borrador del lead desde el dominio de desarrollo: nombres, fronteras de capa,
convenciones de manejo de errores, organización de ficheros y estilo del nuevo módulo de
errores/excepciones y del cambio en `futmondo_client.py`. El borrador es sólido y fiel a
la línea base afirmada; los hallazgos siguientes son huecos que la entrevista humana debe
resolver antes de la integración, no correcciones de prácticas ya afirmadas.

### 1. Ubicación y nombre del nuevo módulo de excepciones tipadas (hueco de organización)

El borrador manda "excepción tipada por modo de fallo, propagada, extendiendo
`SofascoreIPBanError`", pero NO fija **dónde vive la jerarquía nueva ni cómo se llama**. Es
la decisión de organización más consecuente del intent y hoy queda ambigua:

- Hoy `SofascoreIPBanError` está definida **dentro de** `services/sofascore_client.py`
  (acoplada a su cliente). Si la nueva excepción de Futmondo "extiende" a esa, hereda de una
  clase que vive en un cliente hermano — acoplamiento cruzado entre dos clientes con drivers
  HTTP distintos (`requests` vs `curl_cffi`).
- Alternativa coherente con la regla afirmada de **capa/función estrecha testeable**: un
  módulo nuevo `services/integration_errors.py` (o `app/errors.py`) con una raíz común
  (p. ej. `IntegrationError`) de la que cuelguen `FutmondoRequestError` (recuperable),
  `FutmondoFatalError` (fatal), y a la que se re-parente `SofascoreIPBanError` — sin
  ampliar ningún god-file y con superficie de test propia.
- **Pregunta para la entrevista**: ¿la jerarquía nueva vive en un módulo de errores propio
  con una raíz común (`IntegrationError`), o se cuelga literalmente de `SofascoreIPBanError`
  en su fichero actual? De esto depende el naming, el árbol de herencia y el blast radius del
  import.

### 2. Convención de nomenclatura de las excepciones (hueco de naming)

El único precedente afirmado (`SofascoreIPBanError`) mezcla proveedor + causa + sufijo
`Error`. El borrador no fija la convención para las nuevas. Sugiero anclar explícitamente:
sufijo `Error`, PascalCase, nombre por **modo de fallo** (no por status HTTP), en inglés
como el resto de identificadores (regla de idioma ya afirmada). Ejemplos a validar:
`FutmondoTimeoutError`, `FutmondoAuthError`, `FutmondoResponseError`. La entrevista debe
decidir si se nombra por **modo de fallo** (recuperable/fatal semántico) o por **causa
técnica** (timeout/decode/status), porque eso fija cómo el llamador hace el `except <Typed>`.

### 3. Frontera recuperable/fatal en el punto de traducción (hueco de convención)

El borrador dice "recuperable → degrada; fatal → aborta limpio", pero no fija **quién
traduce el modo de fallo a la acción**. Con el contrato nuevo (`_make_request` lanza tipado
en vez de devolver `None`), la decisión recuperable-vs-fatal se toma en el **llamador**
(`sync_*`), no en el cliente. Riesgo de desarrollo concreto: hoy los `sync_*` asumen
`None == sin datos` y siguen; al propagar excepción, un `sync_*` que no capture el nuevo tipo
tumbará el paso completo — cambio de comportamiento silencioso. La convención a afirmar:
el cliente **lanza** el tipo; el llamador **decide** con `except <Typed>` mapeando a
`record_degraded_step` (recuperable) o a abort (fatal). La entrevista debe confirmar que el
mapeo llamador-por-llamador es aceptable dado el blast radius, o si se introduce un helper
único de traducción tipo→acción para no dispersar la política por 1915 líneas.

### 4. Alcance del cambio de contrato de `login()`/getters (hueco de fronteras)

El borrador cita `_make_request` (`None`) pero el hallazgo de RE indica que `login()`
devuelve `bool` y los getters `Optional`. Cambiar `_make_request` a lanzar NO basta si
`login()`/getters siguen colapsando a `bool`/`None`: el modo de fallo tipado se perdería en
la primera capa por encima. La entrevista debe decidir si FR4 endurece **sólo**
`_make_request` (dejando `login`/getters como están, contrato mixto) o **toda la superficie
de señalización de fallo del cliente**. Esto delimita el blast radius real y el número de
llamadores a caracterizar primero.

### 5. `except: pass` de `data_manager_v2.py` — SKIMMED, no confirmado (riesgo de alcance)

El scope-document deja las 29 capturas de `data_sync_service.py` FUERA de alcance, pero los
`except: pass` reales (swallow silencioso) están en `data_manager_v2.py` (L57-58, L68-69,
L672-673) y `photo_service.py` (L475-476), ambos **SKIMMED** en el RE. La regla afirmada
prohíbe swallow silencioso, pero tocarlos implica leer god-files no analizados en
profundidad. La entrevista debe fijar si la primera oleada FR3.2 incluye estos `except: pass`
(y por tanto exige análisis profundo previo de esos ficheros, sin ampliarlos) o si se
difieren. El borrador los menciona sin decidir su inclusión.

### 6. Idioma de mensajes de las excepciones nuevas (matiz de estilo, ya cubierto pero conviene explicitar)

La regla afirmada: identificadores/docstrings en inglés, texto de cara al usuario
(`HTTPException.detail`) en castellano. Una excepción de integración interna NO es texto de
usuario; su mensaje debe ir en **inglés** (es diagnóstico de desarrollador), salvo que se
traduzca a un `HTTPException.detail` en el borde HTTP. El borrador no lo desambigua; conviene
que la integración lo fije para evitar mensajes en castellano dentro de la jerarquía interna.

## Positions

AGREE: La regla "capa/función estrecha testeable, no ampliar god-files ni SQL-en-router" es la frontera de organización correcta y está bien arrastrada.
AGREE: Characterization-first del contrato de `_make_request` antes de cambiarlo es imprescindible por el blast radius alto sobre los llamadores del god-file de sync.
AGREE: "Excepción tipada propagada con `except <Typed>: raise` antes del genérico, nunca `return None` silencioso" es la convención de error-handling correcta y replica fielmente el patrón de referencia.
AGREE: La regla afirmada de NO reformatear brownfield en masa (solo ficheros nuevos o quirúrgico; reviewer sólo `ruff check`) protege el pase de revisión en vuelo y debe mantenerse.
OBJECT: El borrador no fija DÓNDE vive ni CÓMO se nombra la jerarquía de excepciones nueva; "extiende `SofascoreIPBanError`" deja implícito un acoplamiento cross-client que la entrevista debe resolver (ver Contribution §1-2).
OBJECT: El alcance de la señalización de fallo del cliente (¿sólo `_make_request` o también `login()`/getters?) no está delimitado; sin fijarlo el blast radius y los llamadores a caracterizar quedan indefinidos (§4).
