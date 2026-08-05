"""Sofascore sync endpoint — sincroniza ratings de jugadores del mercado actual."""

import logging
from datetime import datetime
from typing import Dict
from fastapi import APIRouter, Query, Depends, HTTPException
from app.core.config import CHAMPIONSHIP_ID
from app.services.futmondo_service import FutmondoService
from app.services.sofascore_client import get_sofascore_client
from app.services.db_connection import get_db

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/sofascore")
async def sync_sofascore(
    championship_id: str = Query(default=CHAMPIONSHIP_ID),
    service: FutmondoService = Depends(FutmondoService),
) -> Dict:
    """Sincroniza ratings de Sofascore para los jugadores del mercado actual.
    
    Busca cada jugador por nombre en Sofascore, obtiene su rating y stats,
    y los guarda en caché.
    """
    try:
        if not service.client or not service.client.is_authenticated():
            service.login()
        client = service.client

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
        now = datetime.now()

        # Limpiar caché anterior de este campeonato
        with db.get_connection() as conn:
            cursor = db.get_cursor(conn)
            sql = "DELETE FROM sofascore_cache WHERE championship_id = ?"
            sql = db.adapt_params(sql)
            cursor.execute(sql, (championship_id,))
            logger.info(f"Sofascore cache cleared for {championship_id}")

        # Collect all results, then batch insert
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
                    player_name, championship_id,
                    full_info.get('id'), full_info.get('name'), full_info.get('team'),
                    full_info.get('rating'), full_info.get('goals'), full_info.get('assists'),
                    full_info.get('appearances'), full_info.get('minutes_played'),
                    full_info.get('yellow_cards'), full_info.get('red_cards'),
                    full_info.get('tournament'), full_info.get('season'),
                    full_info.get('position'), full_info.get('nationality'),
                    full_info.get('age'), full_info.get('successful_dribbles'),
                    full_info.get('accurate_passes_pct'), full_info.get('shots_on_target'),
                    full_info.get('tackles'), full_info.get('interceptions'),
                    full_info.get('clean_sheets'), full_info.get('saves'),
                    full_info.get('sofascore_url', ''),
                    now,
                ))

                synced += 1
                logger.info(f"Sofascore: {player_name} -> rating {full_info.get('rating')}")

            except Exception as e:
                logger.error(f"Sofascore sync error for '{player_name}': {e}")
                errors += 1

        # Batch insert all results at once
        if cache_rows:
            with db.get_connection() as conn:
                cursor = db.get_cursor(conn)
                if db.db_type in ["postgresql", "postgres"]:
                    from psycopg2.extras import execute_values
                    raw_cursor = cursor._cursor if hasattr(cursor, '_cursor') else cursor
                    execute_values(raw_cursor, """
                        INSERT INTO sofascore_cache 
                        (player_name, championship_id, sofascore_id, sofascore_name, team,
                         rating, goals, assists, appearances, minutes_played,
                         yellow_cards, red_cards, tournament, season, position,
                         nationality, age, successful_dribbles, accurate_passes_pct,
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
                            position = EXCLUDED.position,
                            nationality = EXCLUDED.nationality,
                            age = EXCLUDED.age,
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
                         yellow_cards, red_cards, tournament, season, position,
                         nationality, age, successful_dribbles, accurate_passes_pct,
                         shots_on_target, tackles, interceptions, clean_sheets, saves,
                         sofascore_url, synced_at)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, cache_rows)
                logger.info(f"Batch inserted {len(cache_rows)} sofascore records")

        return {
            "success": True,
            "synced": synced,
            "errors": errors,
            "total_players": len(computer_players),
        }
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))
