# Unit Dependency DAG — Fiabilidad backend (FR3.2 + FR4)

Topología de dependencias (no orden de construcción; el orden económico lo fija
Delivery Planning 2.9).

## DAG (prosa)

- `u2-integrations` **depende de** `u1-error-layer`: los clientes tipados y la
  clasificación de fallo de U2 se apoyan en la jerarquía `IntegrationError` y en
  la taxonomía recuperable/fatal establecidas por U1.
- `u1-error-layer` no depende de nada (base).

Grafo acíclico. No hay oportunidades de paralelismo: U2 requiere U1 completa.

## Puntos de integración

- U2 importa las excepciones tipadas definidas en U1 (`IntegrationErrors`).
- U2 reusa el patrón recuperable/fatal endurecido en U1 para clasificar en el
  punto de captura de la ruta de sync.

## Bloque de aristas (machine-readable)

```yaml
units:
  - name: u1-error-layer
    kind: library
    depends_on: []
  - name: u2-integrations
    kind: service
    depends_on: [u1-error-layer]
```

## Assumptions & Open Questions

None.
