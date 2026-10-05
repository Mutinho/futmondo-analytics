# Entities — Modelo del refactor de `data_manager_v2`

> En un refactor de descomposición no se diseñan entidades de datos nuevas: el
> esquema de Neon y los DTOs no cambian. Las "entidades" de este diseño
> funcional son los **artefactos estructurales** que la descomposición produce:
> los módulos-objetivo por responsabilidad y los componentes del patrón DDD de
> referencia que cada extracción instancia. La forma de los datos de dominio
> (players, teams, transactions, …) se preserva verbatim y su fuente de verdad
> sigue siendo el esquema existente; aquí NO se redefine. Fundamentado en
> `requirements.md` (FR1–FR5) y en la superficie real enumerada del god-file.

## Source of truth

```yaml
entities:
  - name: PublicSurface
    description: >
      El contrato público invariante de DataManagerV2 que la descomposición debe
      preservar byte-a-byte (FR1.2). No es un dato: es la frontera de
      infraestructura que todos los consumidores envuelven verbatim.
    attributes:
      - name: constructor
        type: signature
        required: true
        constraints: "DataManagerV2(db_path=None, skip_init=True) — invariante"
      - name: method_count
        type: integer
        required: true
        constraints: "57 (51 public + 6 private); nombres y firmas invariantes"
      - name: private_methods
        type: list
        required: true
        allowed_values:
          - _init_database
          - _ensure_user
          - _get_or_create_user_id
          - _ensure_championship_in_transaction
          - _ensure_schema_updates
          - _get_or_create_user_id
    constraints:
      - "Romper cualquier firma rompe las 4 oleadas DDD y los 8 routers (FR1.2, FR4.1)"

  - name: ResponsibilityModule
    description: >
      Una unidad de extracción: un grupo cohesivo de métodos de DataManagerV2
      por dominio, extraído al patrón DDD de referencia. ~14 instancias (FR1.3).
    attributes:
      - name: name
        type: string
        required: true
        unique: true
        allowed_values:
          - schema-lifecycle
          - players
          - teams-standings
          - performance
          - transactions
          - clauses
          - punishments-bonuses
          - dream-teams-mvp
          - prizes
          - market-roster
          - match-odds
          - news-articles
          - users-stats-evolution
          - sync-metadata-cache
      - name: methods
        type: list
        required: true
        constraints: "subconjunto disjunto de los 57 métodos; la unión cubre los 57"
      - name: coupling_rank
        type: integer
        required: true
        constraints: "orden de extracción menor->mayor acoplamiento (FR1.3, Q1=A); exacto en Plan Approval (FR5.1)"
      - name: extraction_status
        type: enum
        allowed_values: [pending, characterized, extracted, verified]
        defaults: pending
    constraints:
      - "No se añade ningún metodo nuevo al god-file durante la extraccion (FR1.4)"

  - name: DDDLayerComponent
    description: >
      Los componentes que el patron de referencia instancia por cada
      ResponsibilityModule extraido (FR1.1). Molde ya probado en analytics/,
      assistant/, sync/*, prizes/.
    attributes:
      - name: kind
        type: enum
        required: true
        allowed_values: [facade, orchestrator, domain-port, infrastructure-adapter]
      - name: contains_sql
        type: boolean
        required: true
        constraints: "true SOLO para infrastructure-adapter; facade/orchestrator/domain-port nunca (FR1.1)"
      - name: wraps_verbatim
        type: boolean
        constraints: "infrastructure-adapter envuelve el SQL del god-file verbatim, incluida la rama por engine (FR1.4)"

  - name: CharacterizationTest
    description: >
      El test que congela el comportamiento observable de un ResponsibilityModule
      antes de extraerlo (FR2). Usa los fakes in-memory de conftest.py.
    attributes:
      - name: target_module
        type: reference
        references: ResponsibilityModule
        required: true
      - name: asserts_effect
        type: boolean
        required: true
        constraints: "aservera payload/estado/filas/modo-de-fallo observable; nunca assert True (FR2.3)"
      - name: uses_fakes
        type: boolean
        required: true
        constraints: "_FakeInMemoryDB/_FakeCursor/fake_db; sin red, sin BD real, sin credenciales (FR2.1)"
      - name: green_before_and_after
        type: boolean
        required: true
        constraints: "mismas aserciones pasan antes y despues de extraer (FR2.2)"

relationships:
  - from: PublicSurface
    to: ResponsibilityModule
    cardinality: "1:N"
    description: "la superficie se particiona en modulos de responsabilidad disjuntos"
  - from: ResponsibilityModule
    to: DDDLayerComponent
    cardinality: "1:N"
    description: "cada modulo extraido instancia facade/orchestrator/domain-port/infrastructure-adapter"
  - from: CharacterizationTest
    to: ResponsibilityModule
    cardinality: "N:1"
    description: "uno o mas tests congelan el comportamiento de un modulo antes de extraerlo"
```

## Resumen del conjunto de entidades

El modelo captura la **mecánica del refactor**, no datos de negocio nuevos:

- **PublicSurface** — el contrato invariante (constructor + 57 métodos) que es
  la vara de medir de la equivalencia (FR1.2).
- **ResponsibilityModule** — las ~14 unidades de extracción, cada una un
  subconjunto disjunto de los 57 métodos; su unión cubre la superficie completa.
  El orden de extracción va de menor a mayor acoplamiento (FR1.3) y se cierra en
  Plan Approval (FR5.1).
- **DDDLayerComponent** — los 4 componentes del patrón de referencia que cada
  extracción instancia; sólo el `infrastructure-adapter` contiene SQL (FR1.1).
- **CharacterizationTest** — la red de seguridad que congela el comportamiento
  observable antes de cada extracción y debe seguir verde después (FR2).

Las entidades de datos de dominio (players, teams, transactions, clauses,
prizes, …) NO se redefinen: su forma y su esquema en Neon se preservan verbatim
y son fuente de verdad del código existente, no de este artefacto.
