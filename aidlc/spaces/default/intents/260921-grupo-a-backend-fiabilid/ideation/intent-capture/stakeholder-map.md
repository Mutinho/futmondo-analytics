# Mapa de stakeholders — Fiabilidad de la sync de 11 pasos

> Conversation language: Spanish. Intervención backend acotada; sin cambios de
> UI ni de contrato hacia el usuario final más allá de un estado de tarea más
> honesto.

## Stakeholders

| Stakeholder | Interés / preocupación | Impacto del cambio |
|-------------|------------------------|--------------------|
| **Usuario de la app (fantasy manager)** | Que los datos de premios/phantoms sean fiables y que el sync no mienta sobre su resultado | Verá un estado de sync honesto: un paso degradado se refleja como tal, no como éxito silencioso |
| **Operador / mantenedor (tú)** | Diagnóstico rápido de fallos de sync; menos errores tragados | Log estructurado + estado de paso degradado facilitan el triage; menos `except` amplios que esconden la causa |
| **Integración Futmondo (upstream)** | Recibir solo pujas válidas | El techo de sanidad de `price` evita reenviar valores absurdos al proxy |
| **Gate de CI / despliegue** | No promover a producción código con tests no significativos | Nuevas specs `pytest` significativas; suite existente en verde antes de merge |
| **Equipo (reglas afirmadas)** | Coste 0 €, no ampliar god-files, specs significativas | El diseño respeta las tres restricciones por construcción |

## No-stakeholders / fuera de alcance

- **Frontend / UX**: no se toca. La validación de `price` del frontend ya existe
  y es irrelevante para el hueco de backend.
- **Rango dinámico del mercado (min/max)**: fuera de alcance por coste/acoplamiento.
- **Purga masiva de los ~159 `except`**: fuera; solo arranque/migraciones + camino de sync tocado.

## Sources

- Derivado del enunciado de intención (`intent-statement.md`) y de las
  decisiones de encuadre confirmadas por el usuario (Opción C).

## Assumptions & Open Questions

- None.
