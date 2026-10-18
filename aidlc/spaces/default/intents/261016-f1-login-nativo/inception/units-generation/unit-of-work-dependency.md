# Unit of Work — Dependency DAG (F1: Login nativo end-to-end)

> Fase: inception (units-generation). DAG autoritativo de dependencias entre unidades. Idioma:
> castellano; tokens técnicos verbatim en inglés.

```yaml
units:
  - name: backend-refresh-transport
    depends_on: []
  - name: ios-network-client
    depends_on: [backend-refresh-transport]
  - name: ios-native-auth
    depends_on: [ios-network-client]
```

## Diagrama

```mermaid
flowchart LR
    B[backend-refresh-transport] --> N[ios-network-client] --> A[ios-native-auth]
```

Texto (fallback): camino lineal — primero el ajuste de backend, luego el cliente de red Swift,
luego la auth nativa. Sin ciclos; una sola rama.

## Orden de construcción

1. `backend-refresh-transport` (sin dependencias; estabiliza el contrato de transporte).
2. `ios-network-client` (depende de 1).
3. `ios-native-auth` (depende de 2).

## Sources

- [consumes] components.md, decisions.md.

## Assumptions & Open Questions

None.
