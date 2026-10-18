# Intent Backlog — F1: Login nativo end-to-end

> Fase: ideación (scope-definition). Desglose de F1 en unidades de trabajo (capacidades),
> priorización MoSCoW y secuenciación. Idioma: castellano; tokens técnicos verbatim en inglés.

## Priorización (MoSCoW)

| ID | Unidad (capacidad) | MoSCoW | Depende de | Source |
|----|--------------------|--------|------------|--------|
| F1-U1 | Ajuste aditivo del backend para transporte del refresh token (login en body; refresh/logout por body/header) + tests `pytest`. | Must | — | D-01 / Q1=A / Q4=A |
| F1-U2 | Cliente de red Swift: base URL, JSON, inyección de `Bearer`, errores tipados + llamada de humo a `/api/v1/user/me`. | Must | F1-U1 | B-02 / Q2=A |
| F1-U3 | Auth nativa: login UI, intercambio por JWT, access en memoria, refresh token en iOS Keychain, refresh automático, logout. | Must | F1-U1, F1-U2 | B-03 / Q3=A |

## Secuenciación

F1-U1 (backend aditivo, desbloquea el transporte nativo) → F1-U2 (capa de red) → F1-U3 (auth
nativa sobre la capa de red). Es un camino lineal; F1-U1 primero porque sin el transporte del
refresh token por body/header el refresh nativo no funciona.

## Lectura del backlog

- **Must**: las tres unidades; F1 no está "hecho" sin login + refresh + logout nativos.
- No hay Should/Could/Won't dentro de F1 (lo opcional de la app nativa vive en F2/F3 y en el
  backlog del intent de viabilidad).

## Sources

- [consumes] scope-document de F1.
- [backlog] `261016-ios-native-feasibility` (B-02, B-03).
- intent-capture-questions de F1 (Q1=A, Q2=A, Q3=A, Q4=A, Q5=A).

## Assumptions & Open Questions

None.
