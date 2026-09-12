"""Sofascore sync endpoint — sincroniza ratings de jugadores del mercado actual."""

import logging
from datetime import datetime
from typing import Dict, Tuple
from fastapi import APIRouter, Query, HTTPException, Request
from app.core.config import CHAMPIONSHIP_ID
from app.core.constants import SOFASCORE_MIN_COVERAGE_RATIO
from app.api.v1.endpoints._helpers import get_user_futmondo_client
from app.services.sofascore_client import get_sofascore_client, SofascoreIPBanError
from app.services.db_connection import get_db

logger = logging.getLogger(__name__)
router = APIRouter()


def should_apply_replacement(
    synced: int, processed: int, banned: bool, min_ratio: float
) -> Tuple[bool, str]:
    """Decide si aplicar el reemplazo de la caché y devuelve (aplicar, razón).

    Criterio de éxito del repoblado con doble protección (FR2):
    - Si ``banned`` es True → ``(False, "ip_ban")``: se detectó un baneo de IP
      durante el repoblado, se aborta y NO se toca la caché (FR2.2).
    - Si ``processed == 0`` (no había jugadores del computer que procesar) → no
      hay conjunto nuevo que aplicar; se considera ``(False, "below_threshold")``
      para preservar la caché anterior en lugar de vaciarla.
    - Si ``processed > 0`` y ``synced / processed < min_ratio`` (repoblado
      parcial por debajo del umbral) → ``(False, "below_threshold")`` (FR2.4).
    - En cualquier otro caso → ``(True, "ok")``: el repoblado es válido y se
      aplica el reemplazo atómico.

    Es una función pura (sin efectos secundarios ni acceso a BD) para poder
    verificarla de forma aislada.
    """
    if banned:
        return (False, "ip_ban")
    if processed <= 0:
        # Sin jugadores procesados no hay conjunto nuevo válido: no vaciamos la
        # caché anterior. La razón de umbral es la más informativa disponible.
        return (False, "below_threshold")
    if synced / processed < min_ratio:
        return (False, "below_threshold")
    return (True, "ok")


@router.post("/sofascore")
async def sync_sofascore(
    request: Request,
    championship_id: str = Query(default=CHAMPIONSHIP_ID),
) -> Dict:
    """Sincroniza ratings de Sofascore para los jugadores del mercado actual.

    Busca cada jugador por nombre en Sofascore, obtiene su rating y stats, y
    reemplaza la caché ``sofascore_cache`` de forma ATÓMICA (todo-o-nada, FR1):
    primero recolecta todos los resultados del repoblado y solo entonces, dentro
    de UNA sola transacción, ejecuta ``DELETE`` + ``INSERT``. Si el repoblado no
    supera el criterio de éxito (baneo de IP o cobertura por debajo del umbral),
    la caché anterior se conserva intacta y no se ejecuta ningún ``DELETE``.
    """
    try:
        client = get_user_futmondo_client(request)

        # Obtener team_id del usuario
        standings = client.get_matchday_standings(championship_id)
        if not standings or standings.get('error'):
            return {"success": False, "error": "No se pudo obtener standings"}

        teams = standings.get('teams', standings.get('ranking', []))
        user_team_id = ""
        for t in teams:
            if t.get('userid') == client.user_id:
                user_team_id = t.get('teamid') or t.get('id', '')
                break
        if not user_team_id and teams:
            user_team_id = teams[0].get('teamid') or teams[0].get('id', '')

        # Obtener jugadores del mercado
        data = {
            'header': {'token': client.token, 'userid': client.user_id},
            'query': {'championshipId': championship_id, 'userteamId': user_team_id},
            'answer': {}
        }
        resp = client.session.post(f'{client.base_url}/1/market/players', json=data, timeout=15)
        if resp.status_code != 200:
            return {"success": False, "error": "No se pudo obtener mercado"}

        result = resp.json()
        answer = result.get('answer', {})
        all_players = answer if isinstance(answer, list) else answer.get('players', [])

        # Solo jugadores del computer
        computer_players = [p for p in all_players if p.get('computer') is True]

        # Sincronizar con Sofascore
        sofascore = get_sofascore_client()
        db = get_db()
        synced = 0
        errors = 0
        banned = False
        now = datetime.now()

        # FR1.2 / FR2.2: NO se borra la caché aquí. Primero recolectamos todos los
        # resultados del repoblado en memoria; el reemplazo (DELETE + INSERT) se
        # decide y ejecuta después, en una única transacción, solo si el repoblado
        # supera el criterio de éxito. Así un fallo a mitad preserva la caché.
        cache_rows = []

        for p in computer_players:
            player_name = p.get('name', '')
            if not player_name:
                continue

            try:
                # Buscar en Sofascore (con hint del equipo real para mejor matching)
                team_hint = p.get('team', '')
                search_result = sofascore.search_player(player_name, team_hint=team_hint)
                if not search_result or not search_result.get('id'):
                    logger.debug(f"Sofascore: '{player_name}' no encontrado")
                    errors += 1
                    continue

                # Obtener stats completas
                full_info = sofascore.get_player_full_info(search_result['id'])
                if not full_info:
                    errors += 1
                    continue

                cache_rows.append((
                    # championship_id: columna DEPRECADA (FR3.2). Ninguna consulta
                    # de lectura de sofascore_cache filtra por championship_id — la
                    # caché es compartida por jugador, no por campeonato (FR3.1).
                    # Se sigue escribiendo por compatibilidad con el esquema y el
                    # ON CONFLICT actual (FR3.3); su retirada requiere migración de
                    # esquema y queda fuera de alcance.
                    player_name, championship_id,
                    full_info.get('id'), full_info.get('name'), full_info.get('team'),
                    full_info.get('rating'), full_info.get('goals'), full_info.get('assists'),
                    full_info.get('appearances'), full_info.get('minutes_played'),
                    full_info.get('yellow_cards'), full_info.get('red_cards'),
                    full_info.get('tournament'), full_info.get('season'),
                    full_info.get('successful_dribbles'),
                    full_info.get('accurate_passes_pct'), full_info.get('shots_on_target'),
                    full_info.get('tackles'), full_info.get('interceptions'),
                    full_info.get('clean_sheets'), full_info.get('saves'),
                    full_info.get('sofascore_url', ''),
                    now,
                ))

                synced += 1
                logger.info(f"Sofascore: {player_name} -> rating {full_info.get('rating')}")

            except SofascoreIPBanError as ban_exc:
                # FR2.1/FR2.2: baneo de IP detectado. Abortamos el repoblado; el
                # reemplazo NO se aplicará y la caché anterior queda intacta.
                banned = True
                logger.error(f"Sofascore IP ban detectado durante el sync: {ban_exc}")
                break
            except Exception as e:
                logger.error(f"Sofascore sync error for '{player_name}': {e}")
                errors += 1

        # FR2 / FR1.3: evaluar el criterio de éxito. Solo si el repoblado es
        # válido se reemplaza la caché.
        applied, reason = should_apply_replacement(
            synced, len(computer_players), banned, SOFASCORE_MIN_COVERAGE_RATIO
        )

        if applied and cache_rows:
            # FR1.1/FR1.2/NFR1: DELETE + INSERT en UNA sola transacción. Si el
            # INSERT falla, el rollback del context manager revierte el DELETE y
            # la caché anterior sobrevive intacta. Cualquier lectura concurrente
            # ve la caché vieja completa o la nueva completa, nunca un estado
            # parcial.
            with db.get_connection() as conn:
                cursor = db.get_cursor(conn)
                cursor.execute("DELETE FROM sofascore_cache")
                logger.info("Sofascore cache cleared (dentro de la transacción de reemplazo)")

                if db.db_type in ["postgresql", "postgres"]:
                    from psycopg2.extras import execute_values
                    raw_cursor = cursor._cursor if hasattr(cursor, '_cursor') else cursor
                    execute_values(raw_cursor, """
                        INSERT INTO sofascore_cache 
                        (player_name, championship_id, sofascore_id, sofascore_name, team,
                         rating, goals, assists, appearances, minutes_played,
                         yellow_cards, red_cards, tournament, season,
                         successful_dribbles, accurate_passes_pct,
                         shots_on_target, tackles, interceptions, clean_sheets, saves,
                         sofascore_url, synced_at)
                        VALUES %s
                        ON CONFLICT (player_name, championship_id) DO UPDATE SET
                            sofascore_id = EXCLUDED.sofascore_id,
                            sofascore_name = EXCLUDED.sofascore_name,
                            team = EXCLUDED.team,
                            rating = EXCLUDED.rating,
                            goals = EXCLUDED.goals,
                            assists = EXCLUDED.assists,
                            appearances = EXCLUDED.appearances,
                            minutes_played = EXCLUDED.minutes_played,
                            yellow_cards = EXCLUDED.yellow_cards,
                            red_cards = EXCLUDED.red_cards,
                            tournament = EXCLUDED.tournament,
                            season = EXCLUDED.season,
                            successful_dribbles = EXCLUDED.successful_dribbles,
                            accurate_passes_pct = EXCLUDED.accurate_passes_pct,
                            shots_on_target = EXCLUDED.shots_on_target,
                            tackles = EXCLUDED.tackles,
                            interceptions = EXCLUDED.interceptions,
                            clean_sheets = EXCLUDED.clean_sheets,
                            saves = EXCLUDED.saves,
                            sofascore_url = EXCLUDED.sofascore_url,
                            synced_at = EXCLUDED.synced_at
                    """, cache_rows, page_size=50)
                else:
                    cursor.executemany("""
                        INSERT OR REPLACE INTO sofascore_cache 
                        (player_name, championship_id, sofascore_id, sofascore_name, team,
                         rating, goals, assists, appearances, minutes_played,
                         yellow_cards, red_cards, tournament, season,
                         successful_dribbles, accurate_passes_pct,
                         shots_on_target, tackles, interceptions, clean_sheets, saves,
                         sofascore_url, synced_at)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, cache_rows)
                logger.info(f"Batch inserted {len(cache_rows)} sofascore records")
        else:
            # FR1.3/FR2.2/FR2.4: no se supera el criterio de éxito. NO se toca la
            # caché (ni DELETE ni INSERT): la caché anterior queda intacta.
            logger.warning(
                f"Reemplazo de caché Sofascore NO aplicado (reason={reason}, "
                f"synced={synced}, total={len(computer_players)})"
            )

        # FR2.3: respuesta diferenciada. `success` sigue True aunque no se aplique
        # el reemplazo (baneo o umbral), pero `applied` y `reason` permiten al
        # frontend y al cron distinguir cada caso.
        return {
            "success": True,
            "applied": applied,
            "reason": reason,
            "synced": synced,
            "errors": errors,
            "total_players": len(computer_players),
        }
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))
