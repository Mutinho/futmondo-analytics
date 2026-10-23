# Unit Dependency DAG — Sistema de diseño / theming nativo iOS

> Fase: inception. Idioma: castellano; tokens técnicos verbatim en inglés.
> Topología (qué depende de qué). El orden de construcción y el critical path los decide Delivery Planning.

## DAG

- `u2-login-theming` **depende de** `u1-design-system` (usa los tokens y componentes de la librería para revestir el login).
- `u1-design-system` no depende de ninguna otra Unit.

Grafo acíclico.

```
u1-design-system  ──►  u2-login-theming
```

## Puntos de integración

- U2 integra con U1 consumiendo los Color Assets, `DesignTokens` y los componentes (`PrimaryButton`, `TextInputField`, estados) como API interna de la librería.
- U2 integra con el código de login existente de F1 (capa visual), sin tocar su lógica.

## Oportunidades de paralelismo

Ninguna: sólo dos Units con dependencia directa U2→U1, y un único mantenedor. [Q3]

## Edge block

```yaml
units:
  - name: u1-design-system
    kind: library
    depends_on: []
  - name: u2-login-theming
    kind: ui
    depends_on: [u1-design-system]
```

## Assumptions & Open Questions

None.
