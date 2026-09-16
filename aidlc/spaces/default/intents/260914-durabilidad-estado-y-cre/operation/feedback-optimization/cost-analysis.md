# Cost Analysis — Durabilidad del estado

> Etapa Feedback & Optimization (Operation). Análisis de coste del cambio de durabilidad. AWS Cost
> Explorer / Trusted Advisor NO-APLICAN (Fly.io + Neon). Se verifica el mandato dura de coste 0 €.

## Veredicto: coste 0 € — sin cambio

La durabilidad NO introduce ningún coste recurrente nuevo:

| Recurso | Antes | Después | Cambio de coste |
|---------|-------|---------|-----------------|
| Fly.io backend `futmondo-api` | 1 máquina `shared-cpu-1x`/256 MB (free allowance) | Igual | 0 € |
| Fly.io frontend `futmondo-app` | 1 máquina (free allowance) | Igual | 0 € |
| Neon PostgreSQL | Tier free (Frankfurt) | Igual + 2 tablas nuevas (`sync_session`, `sync_task`) de bajo volumen | 0 € (dentro del tier free) |
| GitHub Actions | Free allowance (gate + deploy + crons one-shot) | Igual | 0 € |
| Dependencias nuevas | — | `cryptography` (Fernet) ya disponible; sin paquetes de pago | 0 € |

## Consideraciones de crecimiento (informativo)

- **Neon free**: las 2 tablas nuevas almacenan estado de sesión (por usuario, TTL 12h) y tareas de
  sync (por campeonato). Volumen bajo para uso personal; holgadamente dentro del tier free. Vigilar si
  el número de usuarios/campeonatos creciera mucho.
- **Memoria (256 MB)**: la durabilidad no añade estructuras en memoria significativas; margen para
  `fly scale memory 512` dentro del free allowance si hiciera falta (no esperado).

## Recomendaciones de optimización

- Ninguna acción de reducción de coste necesaria: ya es 0 €.
- Mantener el mandato de coste 0 € en futuras mejoras (regla afirmada en `project.md`).

## No-aplica

- AWS Cost Explorer, Compute Optimizer, Savings Plans, Trusted Advisor: **NO-APLICAN** (no es AWS).
  El control de coste aquí es la disciplina de tiers gratuitos, no una herramienta de FinOps de pago.
