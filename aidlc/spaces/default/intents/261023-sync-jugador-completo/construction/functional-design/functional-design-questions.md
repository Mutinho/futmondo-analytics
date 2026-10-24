# Functional Design — Preguntas

Intent `261023-sync-jugador-completo`. Las decisiones de diseño están muy
acotadas por los requisitos aprobados; se confirman aquí. Cada ⭐ es la
recomendación.

---

## Q1. Punto de normalización de home/away average

- A. ⭐ Normalizar en el **orquestador del sync** (al construir `player_records`)
  con `clean_float`, convirtiendo `"NaN"`/vacío/null/no-parseable → `None`, para
  persistir ya el valor limpio. (BR1.2, addresses advisory M-FR1.3)
- X. Other (please specify)

[Answer]: A

---

## Q2. Peor caso de equipo/escudo (teamId sin entrada ni real_team_name)

- A. ⭐ Servir `team=''` y `team_logo=''` (igual que el contrato produce hoy ante
  equipo ausente); el front lo degrada con elegancia. (BR3.1, addresses M-FR3.1)
- X. Other (please specify)

[Answer]: A

---

## Q3. Defaults hasta el primer sync

- A. ⭐ `points=0`, `change=0`, `home_average=None`, `away_average=None`,
  `matches=0`, `status=''` — idénticos a los defaults actuales del contrato;
  el sync periódico completa los valores reales; sin backfill forzado.
  (BR5.2, addresses M-NFR5)
- X. Other (please specify)

[Answer]: A

---

## Q4. Alcance de la caracterización (NFR2)

- A. ⭐ Congelar: (a) campos que persiste el orquestador en player_records/stats;
  (b) forma del contrato de favorites/my; (c) selección de favoritos (fav True
  AND no userteamId); (d) no-leak de credenciales. (BR5.1, addresses M-NFR2)
- X. Other (please specify)

[Answer]: A

---

## Consolidated Summary Confirmation

Resumen del diseño (Todas A):

- **Esquema:** +6 columnas en `players` vía `ALTER TABLE ... ADD COLUMN IF NOT
  EXISTS` idempotente, en el punto de evolución de esquema existente (sin god-files).
- **Sync:** el orquestador extrae `points/change/home/away/matches/status`;
  home/away normalizados con `clean_float` (NaN/vacío/null → None).
- **Lectura:** `favorites_read` sirve esos campos desde `players`; `team/team_logo`
  por `teamId` con `LALIGA_TEAMS` (peor caso `''`); contrato y orden intactos;
  defaults hasta el primer sync.
- **Calidad:** characterization-first (4 ramas enumeradas); contrato inmutable;
  coste 0; gate verde; `market/today` no se toca.

[Answer]: Looks correct
