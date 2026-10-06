# Entities — calculator-toggle

Unidad: `calculator-toggle` (frontend-only). Esta mejora **no introduce entidades
de datos nuevas ni persistencia de dominio**: trabaja sobre datos que ya carga la
pantalla. El único "estado" nuevo es una **preferencia de UI** (value object
efímero del cliente, persistida en `localStorage`). Los conceptos de cálculo
(roster, mercado, jugadores en venta, pujas) son datos de solo lectura ya
existentes, modelados aquí como contexto para fijar los términos del cálculo.

```yaml
entities:
  - name: IncludeOnSalePreference
    kind: value_object
    description: Preferencia de UI que indica si los jugadores en venta se incluyen en la proyección de saldo futuro de la Calculadora.
    persistence: localStorage (cliente); NO toca backend ni base de datos
    attributes:
      - name: includeOnSale
        type: boolean
        required: true
        default: true
        constraints: "Un valor corrupto/ausente/no parseable se interpreta como true (ver BR3.x)."
    storage:
      medium: localStorage
      key: "futmondo_calc_include_onsale"
      format: "cadena 'true' | 'false'"
    constraints:
      - "Inmutable por valor: cambiar la preferencia reemplaza el valor, no muta un identificador (no hay identidad de entidad)."
    relationships:
      - "Modula el término onSaleTotal en el cálculo de FutureBalanceProjection (ver functional-spec.md)."

  - name: FutureBalanceProjection
    kind: value_object
    description: Resultado derivado y reactivo que proyecta el saldo futuro del usuario a partir de datos ya cargados. No se persiste.
    persistence: ninguna (derivado en memoria vía computed signals)
    attributes:
      - name: balance
        type: money
        required: true
        constraints: "Saldo actual; dato de solo lectura de GET /api/v1/market/today (user_info.balance)."
      - name: selectedTotal
        type: money
        required: true
        constraints: "Suma del valor proyectado de los jugadores seleccionados para vender."
      - name: onSaleTotal
        type: money
        required: true
        constraints: "Suma del valor de los jugadores ya en venta; se incluye en el cálculo solo si includeOnSale = true."
      - name: activeBidsTotal
        type: money
        required: true
        constraints: "Dinero comprometido en pujas activas; SIEMPRE resta (invariante, BR2.1)."
      - name: futureBalance
        type: money
        required: true
        constraints: "Derivado (ver BR1.x): balance + selectedTotal + (includeOnSale ? onSaleTotal : 0) - activeBidsTotal."
    relationships:
      - "Depende de IncludeOnSalePreference para decidir si onSaleTotal entra en la suma."
      - "IncludeOnSalePreference tambien gobierna la composicion de la lista seleccionable (incluir/excluir jugadores en venta) y la visibilidad del bloque 'En venta' (FR5)."
```

## Resumen del modelo

El conjunto de entidades es deliberadamente mínimo porque la unidad es una mejora
de UI sobre datos existentes:

- **IncludeOnSalePreference**: value object nuevo, única pieza de estado que la
  mejora añade; vive en `localStorage` del navegador, nunca en el backend.
- **FutureBalanceProjection**: cálculo derivado ya existente en el componente
  (`computed()` de signals); se documenta aquí porque sus términos y la
  condición sobre `onSaleTotal` son el núcleo de la mejora. No se persiste.

No hay entidades de base de datos, migraciones ni modelos de dominio backend en
esta unidad (frontend-only; confirmado contra `calculator.component.ts`).

## Sources

- `requirements.md` (FR1–FR4, FR3.1–FR3.4, A1–A3).
- `codekb/futmondo-analytics/architecture.md` (fórmula de `futureBalance`).
- Código real: `angular-app/src/app/features/calculator/calculator.component.ts`
  (`onSaleTotal`, `futureBalance`, patrón `localStorage` `futmondo_view_calculator`).

## Assumptions & Open Questions

None.
