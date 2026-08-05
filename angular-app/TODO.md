# Mejoras Pendientes — Futmondo Angular

## Selector de Campeonato (prioritario)
- [ ] Añadir selector de campeonato en el sidebar o toolbar
  - Campeonato 1: `592416daa3a2dd871a7a9956` — "Ivan el flautista de Futmondin" (sin cláusulas, 200M, 7 equipos)
  - Campeonato 2: `6a5f82a09c06c8d0ceaa40ee` — "Infantino es español" (con cláusulas, 300M, 6 equipos)
- [ ] Crear tabla/config en DB con metadata de campeonatos (nombre, tiene_clausulas, presupuesto_inicial, excluded_teams)
- [ ] Ocultar tab "Clausulables" y sub-tab "Mercado" cuando el campeonato activo no tenga cláusulas
- [ ] Todos los servicios deben recibir el championship_id del campeonato seleccionado

## Presupuesto
- [ ] Implementar ordenación funcional en mat-table (MatSort con MatTableDataSource)
- [ ] Al pulsar "Sincronizar", abrir un MatDialog con progreso/resultado del sync (transacciones nuevas, errores, duración)

## Estadísticas
- [ ] Al pulsar la barra de un equipo en los gráficos, abrir un modal/dialog con los movimientos de ese equipo
