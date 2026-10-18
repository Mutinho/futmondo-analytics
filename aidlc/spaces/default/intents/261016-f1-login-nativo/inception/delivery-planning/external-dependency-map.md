# External Dependency Map — F1: Login nativo end-to-end

> Fase: inception (delivery-planning). Dependencias externas al código de F1. Idioma: castellano;
> tokens técnicos verbatim en inglés.

| Dependencia | Tipo | Estado | Impacto / mitigación |
|-------------|------|--------|----------------------|
| Backend FastAPI (`futmondo-api`) en producción | Interna reutilizada | Disponible | Bolt 1 lo ajusta de forma aditiva; no se despliega nada nuevo de infra. |
| API Futmondo (externa) | Servicio externo | Disponible (ya usado por el backend) | F1 no la llama directamente; el backend valida credenciales contra ella como hoy. |
| Cadena de build nativa (WSL + Swift 6.4 + usbmuxd + `xtool`) | Toolchain | Satisfecha (spike F0) | Bolts 2/3 se construyen/instalan con la cadena ya validada. |
| Apple ID gratuito (firma) | Cuenta | Disponible | Firma gratuita; caducidad ~7 días (B-09, fuera de F1). |
| Gate de CI (GitHub Actions) + Fly.io | Pipeline | Operativo | Bolt 1 pasa el gate bloqueante antes de `main`. |
| iPhone 13 Pro físico | Dispositivo | Disponible | Validación manual de Bolt 3 (NFR-3). |

## Dependencias de pago / coste

Ninguna recurrente nueva (coste 0 €). La única excepción conocida del proyecto (Apple Developer
Program ~99 €/año) **no aplica a F1**: se usa firma gratuita.

## Sources

- [consumes] external context del intent de viabilidad; constraint-register de F1; team-practices.

## Assumptions & Open Questions

None.
