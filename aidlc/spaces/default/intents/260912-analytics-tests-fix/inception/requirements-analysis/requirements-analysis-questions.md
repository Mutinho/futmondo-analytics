# Requirements Analysis — Preguntas de Clarificación

Contexto: bugfix acotado. Reverse Engineering ya diagnosticó dos causas de los
3 tests rojos en `backend/tests/test_analytics_service.py`:
(1) el fixture reemplaza `__init__` por un `fake_init` que omite `_team_cache`
y `_player_cache` → `AttributeError` en `test_championship_trends` y
`test_clause_network`; (2) el servicio emite `last_transaction_price` pero el
test exige `latest_price` → `KeyError` en `test_player_value_trend`.

## Q1: Estrategia de arreglo

¿Dónde debe aplicarse el arreglo?

- A. En el TEST (Alternativa A, recomendada, mínimo impacto): inicializar `_team_cache`/`_player_cache` en el `fake_init` del fixture y alinear la aserción de `test_player_value_trend` con la clave real `last_transaction_price`. No se toca el servicio ni su contrato.
- B. En el SERVICIO (Alternativa B): añadir/renombrar la clave a `latest_price` y/o endurecer los helpers ante caches ausentes. Implica verificar los consumidores `/api/v1/analytics/*`.
- C. Mixto: arreglar los caches en el test (A) pero renombrar la clave a `latest_price` en el servicio (B) por considerarlo el nombre correcto del contrato.
- X. Other (please specify)

[Answer]: A

## Q2: Alcance de la verificación

Además de los 3 tests, ¿qué debe quedar verificado como criterio de éxito?

- A. Toda la suite de pytest del backend en verde (los 3 arreglados + los otros 3 del fichero + el resto de ficheros de caracterización), sin tocar el frontend.
- B. Solo los 3 tests objetivo en verde.
- C. Suite de pytest en verde + confirmar que el gate `verify` de `fly-deploy.yml` (pytest + ng test) pasaría.
- X. Other (please specify)

[Answer]: A

## Consolidated Summary Confirmation

- Estrategia de arreglo: en el TEST (Alternativa A). Inicializar `_team_cache`/`_player_cache` en el `fake_init` del fixture y alinear la aserción de `test_player_value_trend` con la clave real `last_transaction_price`. No se toca el servicio ni su contrato de salida.
- Alcance de verificación: toda la suite de pytest del backend en verde (los 3 tests objetivo + los otros 3 del fichero + el resto de ficheros de caracterización), sin tocar el frontend.

Does this all look correct before I generate the requirements artifact?

- Looks correct
- Request changes

[Answer]: Looks correct
