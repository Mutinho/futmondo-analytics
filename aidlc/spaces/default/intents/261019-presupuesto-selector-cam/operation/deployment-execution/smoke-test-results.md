# Smoke Test Results — F2

> Fase: operación. Idioma: castellano; tokens técnicos verbatim en inglés.

## Smoke manual en dispositivo (iPhone 13 Pro)

Tras instalar, el propietario verificó el camino feliz de F2:

- Login (F1) → aterrizaje en **Presupuesto** (tab bar flotante). ✅
- Lista de equipos con cards neón-glass, saldo/rendimiento/puja máxima/premios. ✅
- **Selector de campeonato** (trofeo) cambia de liga y recarga. ✅
- **Ordenar** (hoja) reordena. ✅
- **Detalle de equipo**: zoom, summary, Compras/Ventas, entrada escalonada. ✅
- **Logout** (menú ···) vuelve a login. ✅

No hay smoke de servidor (F2 no despliega backend). El smoke `/health` del backend sigue siendo el del pipeline existente, no invocado por F2.

## Assumptions & Open Questions

None.
