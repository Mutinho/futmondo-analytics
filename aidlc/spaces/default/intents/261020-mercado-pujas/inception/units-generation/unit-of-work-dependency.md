# Unit of Work — Dependencias (DAG) — F3 Mercado

> Topología de dependencias entre unidades (aristas dirigidas "A depende de B"),
> cycle-free. NO recomienda orden de implementación ni ruta crítica: eso es
> decisión económica de Delivery Planning (2.9), que consume este DAG.

## Sources

- `.../inception/units-generation/unit-of-work.md`.
- `.../inception/domain-design/components.md`, `decisions.md`.

## DAG

F3 define **una sola unidad** (`u1-market`). No hay dependencias de unidad
nuevas: `u1-market` sólo se apoya en componentes **ya existentes** del paquete
`ios/` (F1/F2) —`NetworkClient`, `AuthService`/sesión, `DesignSystem`,
`RootTabView`—, que son estado del repo, no unidades de este intent. Por tanto:

```
u1-market  (depends_on: [])
```

Fallback de texto: el grafo tiene un único nodo `u1-market` sin aristas
salientes; no hay ciclos (trivialmente) ni dependencias entre unidades nuevas.

### Bloque de aristas (fuente de verdad machine-readable)

```yaml
units:
  - name: u1-market
    kind: ui
    depends_on: []
```

## Puntos de integración entre unidades

Ninguno **entre unidades de F3** (sólo hay una). Los puntos de integración de
`u1-market` son hacia componentes existentes (fuera del alcance de unidades
nuevas):

- `NetworkClient` (F1) — transporte HTTP con `Authorization: Bearer`.
- `AuthService` / sesión autenticada (F1) — provee el access token.
- `DesignSystem` (F1/F2) — tokens y componentes de UI reutilizados.
- `RootTabView` (F1/F2) — shell de pestañas que `u1-market` extiende con la 2ª
  pestaña.
- Contratos backend existentes: `/api/v1/market/{today,bid,cancelbid}`,
  `/api/v1/sofascore/player/{name}` (sin cambios de servidor).

## Oportunidades de desarrollo en paralelo

No aplica: una sola unidad. (Dentro de `u1-market`, la lógica `FutmondoKit` y
las vistas `FutmondoApp` tienen un orden intra-unidad test-after, pero no son
unidades independientes.)

## Walking skeleton

No aplica (línea base OFF; el sistema ya está en producción y la capa `ios/`
existe desde F1). `u1-market` no es un esqueleto a bootstrap-ear: añade una
pantalla a un shell ya existente.

## Assumptions & Open Questions

None.
