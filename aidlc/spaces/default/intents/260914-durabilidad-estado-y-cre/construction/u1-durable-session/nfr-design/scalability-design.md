# Scalability Design — u1-durable-session

> Etapa NFR Design (Construction). Traduce NFR5.2 (tolerar multi-instancia) en un diseño concreto,
> acotado por la restricción de coste 0€ (NFR3). Es diseño, no implementación.

## Sources

- nfr-requirements/scalability-requirements.md (NFR5.2 esc.) [scope]
- team.md (Fly.io min=max=1; Neon free; coste 0€) [scope]
- nfr-design-questions.md (Q3-A lock BD como autoridad de concurrencia) [Q3]
- functional-design/functional-spec.md (BR1.5 BD autoridad, BR1.1 lock por usuario) [scope]

## Principio de escalado

**Diseño sin estado autoritativo en memoria de proceso.** Toda la autoridad de estado y de
concurrencia vive en la base de datos (Neon), no en la memoria del proceso `futmondo-api`. Esto hace
que el diseño **tolere más de una instancia** aunque hoy `fly.toml` fije `min=max=1` (NFR5.2), sin
necesidad de rediseño futuro.

- La caché `SessionStore` en memoria es **best-effort** (BR1.5): acelera, pero no es fuente de verdad.
  Dos instancias con cachés distintas convergen porque ambas leen/escriben la misma fila de BD.
- La concurrencia se serializa con lock de BD (`SELECT ... FOR UPDATE`, Q3-A), que funciona **entre
  instancias**, no solo dentro de un proceso. Un lock en memoria NO se eligió precisamente porque no
  cruzaría instancias.

## Distribución de carga

Sin cambios: nginx delante, una instancia hoy. El diseño no exige afinidad de sesión (sticky
sessions) porque no hay estado autoritativo en memoria — cualquier instancia puede atender cualquier
petición leyendo la sesión de la BD. Esto es lo que habilitaría escalar horizontalmente sin tocar el
código.

## Particionado de datos

No aplica. La tabla de sesión es de **una fila por usuario** (upsert), sin crecimiento no acotado. El
volumen es el actual (sesiones por usuario, TTL 12h) y Neon free lo absorbe sin acercarse a los
límites del tier. La purga perezosa (Q5-A) mantiene la tabla en ~1 fila por usuario activo.

## Umbrales de capacidad y auto-scaling

- **Sin reglas de auto-scaling nuevas** ni triggers: el intent es una intervención acotada; el volumen
  no cambia. Definir escalado automático sería sobre-ingeniería y podría implicar coste (NFR3).
- **Sin réplicas de lectura, sin caché externo (Redis), sin servicios Fly.io nuevos** — todos
  implicarían coste recurrente, prohibido por la regla dura de coste 0€.

## Camino de escalado futuro (documentado, no implementado)

Si algún día se subiera a `min>1`:
1. El diseño ya lo soporta: BD como autoridad, sin estado en memoria, lock cross-instancia.
2. El único ajuste sería `fly.toml` (`min`/`max`), no el código de la sesión.
3. Neon (con pooling) toleraría la concurrencia adicional dentro del tier hasta sus límites.

No se toma esa decisión ahora; se deja el diseño preparado para no bloquearla.

## Trazabilidad

| NFR | Solución de diseño |
|-----|--------------------|
| NFR5.2 (esc.) | Sin estado autoritativo en memoria; BD como autoridad de estado y concurrencia (lock cross-instancia, Q3-A); sin sticky sessions requeridas |
