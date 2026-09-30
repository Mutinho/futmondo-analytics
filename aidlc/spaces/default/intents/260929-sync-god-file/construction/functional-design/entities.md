# Entities — Descomposición DDD de `data_sync_service.py`

> Etapa de diseño (refactor, depth Minimal). Modelo técnico-agnóstico de las
> entidades y value objects del dominio de sincronización tras la descomposición.
> No es esquema de BD: el esquema de Neon no cambia (FR out-of-scope). Estas son
> las abstracciones de dominio que estructuran cada módulo `sync_<domain>` nuevo.

```yaml
entities:
  - name: SyncResult
    description: >
      Value object inmutable que devuelve cada operacion sync_* y que sync_all()
      agrega. Es el contrato de payload observable a preservar byte-a-byte (FR5.1).
    attributes:
      - name: status
        type: enum
        required: true
        allowed_values: [success, no_new_data, closed, no_config, no_teams,
          no_standings, no_rounds, no_prizes_configured, error]
        notes: >
          Conjunto observable EXACTO verificado en data_sync_service.py: el exito
          es "success" (no "ok"). Ademas del comun (success/no_new_data/error),
          hay variantes por dominio ya presentes hoy: "closed" (rondas),
          "no_config"/"no_prizes_configured" (prizes), "no_teams"/"no_standings"/
          "no_rounds" (rankings/standings). No se renombra ni se reduce el
          conjunto observado por dominio (FR5.1, BR3.2).
      - name: records_synced
        type: integer
        required: true
        min: 0
      - name: duration_seconds
        type: number
        required: false
      - name: last_sync_id
        type: string
        required: false
        notes: Presente solo en dominios incrementales (p. ej. transactions).
      - name: error
        type: string
        required: false
        notes: Presente solo cuando status == error (red final BR2.2).
    constraints:
      - La forma exacta (claves presentes/ausentes) de cada dominio se congela
        con caracterizacion antes de extraer (FR4, FR5.1).

  - name: SyncAllReport
    description: >
      Value object que devuelve sync_all(): mapea cada dominio a su SyncResult
      bajo claves literales fijas.
    attributes:
      - name: entries
        type: map<string, SyncResult>
        required: true
        notes: >
          Exactamente 10 claves literales, en este orden de ejecucion:
          players, transactions, clauses, punishments_bonuses, dream_teams,
          player_performance, rosters, team_standings, match_odds, prizes.
    constraints:
      - Las 10 claves son literales y NO se renombran (FR5.1.1). El dominio
        rankings (operacion sync_round_rankings) expone su SyncResult bajo la
        clave team_standings; nombre de dominio y clave difieren y ambos se
        preservan.
      - El orden de insercion (players primero por FK) se preserva (FR5.2).

  - name: SyncDomain
    description: >
      Abstraccion de diseno (no runtime) que representa cada uno de los 10
      dominios de sync extraidos a su propio modulo de aplicacion.
    attributes:
      - name: name
        type: string
        required: true
        allowed_values: [players, transactions, clauses, punishments, dream_teams,
          performance, rosters, rankings, odds, prizes]
      - name: public_operation
        type: string
        required: true
        notes: >
          El metodo sync_* que el facade delega a este dominio. Mapa:
          players->sync_players_full, transactions->sync_transactions,
          clauses->sync_clauses, punishments->sync_punishments_bonuses,
          dream_teams->sync_dream_teams_mvps, performance->sync_player_performance,
          rosters->sync_rosters, rankings->sync_round_rankings,
          odds->sync_match_odds, prizes->sync_prizes.
      - name: shape
        type: enum
        required: true
        allowed_values: [full-layered, lightweight]
        notes: >
          full-layered = domain/ports + application + infrastructure/*_adapter +
          entry (calculo/SQL sustancial); lightweight = orquestador fino +
          adaptador/funcion estrecha (casi passthrough). Decidido por dominio
          en diseno (Q1); el SQL siempre queda tras la frontera testeable en
          ambas formas.
      - name: data_port
        type: reference
        references: SyncDataPort
        required: true
    relationships:
      - SyncDomain 1..1 --produces--> SyncResult
      - SyncDomain 1..1 --depends-on--> SyncDataPort (uno estrecho por dominio)

  - name: SyncDataPort
    description: >
      Value object de diseno: el Protocol consumer-owned, estrecho, que cada
      dominio define en su capa domain (patron AnalyticsDataPort). Declara solo
      las operaciones de DataManagerV2 y los cursor.execute inline que ese
      dominio consume. Es la frontera de inversion de dependencias que hace el
      calculo testeable con fakes en memoria (FR3.1).
    attributes:
      - name: operations
        type: list<method-signature>
        required: true
        notes: >
          Subconjunto minimo por dominio; en dominios lightweight puede ser de
          una o dos operaciones. Implementado por un *_adapter de infraestructura
          que envuelve DataManagerV2 sin reescribirlo (FR3.2).
    relationships:
      - SyncDataPort <--implements-- DomainDataAdapter (infrastructure)

  - name: IntegrationFailureMode
    description: >
      Value object de diseno que clasifica el fallo de integracion externa,
      preservando la semantica BR2.1-2.3 observable hoy. No es tipo nuevo: son
      las excepciones Integration*Error ya existentes.
    attributes:
      - name: kind
        type: enum
        required: true
        allowed_values: [recoverable, fatal]
      - name: exception_type
        type: string
        required: true
        allowed_values: [IntegrationBanError, IntegrationTimeoutError,
          IntegrationUnparseableError, IntegrationRequestError]
      - name: non_sensitive_context
        type: map
        required: false
        notes: >
          status/endpoint, NUNCA password ni token (regla afirmada
          no-credenciales-en-excepciones).
    constraints:
      - recoverable en punto de escritura escala a fatal (BR2.3): PROPAGATE para
        abortar limpio en vez de degradar sobre una escritura que podria
        corromper datos.
```

## Resumen del modelo de entidades

El modelo es deliberadamente pequeño porque es un **refactor de estructura, no de
datos**: el esquema de Neon y las tablas no cambian. Las entidades son las
abstracciones de dominio que dan forma a los módulos nuevos:

- **`SyncResult`** y **`SyncAllReport`** son el **contrato de payload observable**
  que la equivalencia funcional estricta debe preservar (FR5.1, FR5.1.1) — con las
  10 claves literales y el orden fijo.
- **`SyncDomain`** modela cada uno de los 10 dominios extraídos, con su forma
  (`full-layered` vs `lightweight`, Q1) y su `public_operation` (el `sync_*` que el
  facade le delega).
- **`SyncDataPort`** es el `Protocol` estrecho consumer-owned por dominio (Q2),
  frontera de inversión de dependencias que aísla el SQL en el adaptador (FR3).
- **`IntegrationFailureMode`** captura la clasificación recuperable/fatal
  (BR2.1–2.3) que vive en el orquestador del dominio (Q3, Q4) y que la
  caracterización congela (FR5.3).

Las reglas de negocio asociadas (equivalencia, orden, errores, escritura atómica)
están en `rules.md`; los workflows y la máquina de estados, en `functional-spec.md`.
