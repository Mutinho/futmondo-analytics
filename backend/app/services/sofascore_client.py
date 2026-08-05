"""
Sofascore API Client — Obtiene ratings y estadísticas de jugadores.
Usa curl_cffi para bypass de TLS fingerprinting.
"""

import logging
import time
from typing import Optional, Dict, List
from curl_cffi import requests as cffi_requests

logger = logging.getLogger(__name__)

BASE_URL = "https://api.sofascore.com/api/v1"


class SofascoreClient:
    """Client para la API no oficial de Sofascore."""

    def __init__(self):
        self.session = cffi_requests.Session(impersonate="chrome")
        self._last_request = 0
        self._min_delay = 0.75  # 750ms entre requests (Sofascore tolera bien)

    def _throttle(self):
        """Rate limiting para no ser baneado."""
        elapsed = time.time() - self._last_request
        if elapsed < self._min_delay:
            time.sleep(self._min_delay - elapsed)
        self._last_request = time.time()

    def _get(self, endpoint: str) -> Optional[Dict]:
        """GET request con throttling y error handling."""
        self._throttle()
        url = f"{BASE_URL}{endpoint}"
        try:
            resp = self.session.get(url, timeout=10)
            if resp.status_code == 200:
                return resp.json()
            elif resp.status_code == 404:
                return None
            else:
                logger.warning(f"Sofascore {resp.status_code} for {endpoint}")
                return None
        except Exception as e:
            logger.error(f"Sofascore request error: {e}")
            return None

    def search_player(self, name: str, team_hint: Optional[str] = None) -> Optional[Dict]:
        """Busca un jugador por nombre. Si se pasa team_hint, prioriza resultados de ese equipo."""
        self._throttle()
        url = f"{BASE_URL}/search/players"
        try:
            resp = self.session.get(url, params={"q": name}, timeout=10)
            if resp.status_code != 200:
                logger.warning(f"Sofascore search {resp.status_code} for '{name}'")
                return None

            data = resp.json()
            results = data.get("results", [])

            if not results:
                return None

            # Si hay team_hint, intentar encontrar uno que coincida
            if team_hint:
                team_hint_lower = team_hint.lower()
                for r in results:
                    entity = r.get("entity", r)
                    entity_team = (entity.get("team", {}) or {}).get("name", "")
                    if entity_team and team_hint_lower in entity_team.lower():
                        return {
                            "id": entity.get("id"),
                            "name": entity.get("name"),
                            "slug": entity.get("slug"),
                            "team": entity_team,
                            "position": entity.get("position"),
                        }

            # Fallback: primer resultado
            entity = results[0].get("entity", results[0])
            return {
                "id": entity.get("id"),
                "name": entity.get("name"),
                "slug": entity.get("slug"),
                "team": entity.get("team", {}).get("name") if entity.get("team") else None,
                "position": entity.get("position"),
            }
        except Exception as e:
            logger.error(f"Sofascore search error for '{name}': {e}")
            return None

    def get_player_stats(self, player_id: int) -> Optional[Dict]:
        """Obtiene estadísticas del jugador con prioridad:
        1. Temporada actual (25/26 o 26/27) en LaLiga / LaLiga 2
        2. Temporada anterior en LaLiga / LaLiga 2
        3. Cualquier liga de club de la temporada actual
        4. Cualquier liga de club de la temporada anterior
        """
        data = self._get(f"/player/{player_id}/statistics/seasons")
        if not data:
            return None

        seasons = data.get("uniqueTournamentSeasons", [])
        if not seasons:
            return None

        # Torneos a excluir (selecciones/copas internacionales)
        EXCLUDED_KEYWORDS = {'world cup', 'euro ', 'copa america', 'nations league', 'friendlies', 'olympic'}
        
        # Temporadas relevantes (actual y anterior)
        CURRENT_SEASON_KEYWORDS = ['25/26', '26/27', '2026']
        PREVIOUS_SEASON_KEYWORDS = ['24/25', '2025']
        
        # Ligas prioritarias
        PRIORITY_KEYWORDS = ['laliga', 'la liga']

        # Clasificar candidatos por prioridad
        # (prioridad, tournament, season)  — menor número = mayor prioridad
        candidates = []

        for tournament_season in seasons:
            tournament = tournament_season.get("uniqueTournament", {})
            tournament_name = (tournament.get("name") or "").lower()
            
            # Excluir selecciones
            if any(kw in tournament_name for kw in EXCLUDED_KEYWORDS):
                continue

            seasons_list = tournament_season.get("seasons", [])
            for season in seasons_list[:2]:  # Solo las 2 temporadas más recientes de cada torneo
                season_name = (season.get("name") or "").lower()
                
                is_priority_league = any(kw in tournament_name for kw in PRIORITY_KEYWORDS)
                is_current = any(kw in season_name for kw in CURRENT_SEASON_KEYWORDS)
                is_previous = any(kw in season_name for kw in PREVIOUS_SEASON_KEYWORDS)

                if is_priority_league and is_current:
                    priority = 1
                elif is_priority_league and is_previous:
                    priority = 2
                elif is_current:
                    priority = 3
                elif is_previous:
                    priority = 4
                else:
                    priority = 5

                candidates.append((priority, tournament, season))

        # Ordenar por prioridad
        candidates.sort(key=lambda x: x[0])

        # Probar cada candidato hasta encontrar stats con rating
        for priority, tournament, season in candidates:
            season_id = season.get("id")
            tournament_id = tournament.get("id")

            stats = self._get(
                f"/player/{player_id}/unique-tournament/{tournament_id}/season/{season_id}/statistics/overall"
            )
            if stats and stats.get("statistics"):
                stat_data = stats["statistics"]
                # Solo aceptar si tiene rating o al menos partidos jugados
                if stat_data.get("rating") or (stat_data.get("appearances") and stat_data["appearances"] >= 3):
                    return {
                        "tournament": tournament.get("name", ""),
                        "season": season.get("name", ""),
                        "stats": stat_data,
                    }

        return None

    def get_player_rating(self, player_id: int) -> Optional[float]:
        """Obtiene el rating medio del jugador."""
        stats = self.get_player_stats(player_id)
        if stats and stats.get("stats"):
            rating = stats["stats"].get("rating")
            if rating:
                return rating
        # Fallback: calcular media de últimos partidos
        return self.get_player_rating_from_matches(player_id)

    def get_player_rating_from_matches(self, player_id: int) -> Optional[float]:
        """Calcula rating medio a partir de los últimos partidos jugados (máximo 6 meses atrás)."""
        import time as _time
        data = self._get(f"/player/{player_id}/events/last/0")
        if not data:
            return None

        stats_map = data.get("statisticsMap", {})
        events = data.get("events", [])

        # Solo partidos de los últimos 6 meses
        six_months_ago = _time.time() - (180 * 24 * 3600)

        ratings = []
        for event in events[:20]:
            # Verificar fecha del partido
            start_timestamp = event.get("startTimestamp", 0)
            if start_timestamp < six_months_ago:
                break  # Los eventos están ordenados por fecha, podemos parar

            event_id = str(event.get("id"))
            stats = stats_map.get(event_id, {})
            rating = stats.get("rating")
            if rating:
                ratings.append(rating)

        if len(ratings) >= 3:  # Mínimo 3 partidos para que sea significativo
            return sum(ratings) / len(ratings)
        return None

    def get_player_full_info(self, player_id: int) -> Optional[Dict]:
        """Obtiene info completa: perfil + stats + rating."""
        # Perfil
        profile = self._get(f"/player/{player_id}")
        if not profile:
            return None

        player_data = profile.get("player", {})

        # Stats
        stats_data = self.get_player_stats(player_id)

        result = {
            "id": player_id,
            "name": player_data.get("name", ""),
            "slug": player_data.get("slug", ""),
            "sofascore_url": f"https://www.sofascore.com/football/player/{player_data.get('slug', '')}/{player_id}",
            "position": player_data.get("position", ""),
            "team": player_data.get("team", {}).get("name") if player_data.get("team") else None,
            "nationality": player_data.get("country", {}).get("name") if player_data.get("country") else None,
            "age": player_data.get("age"),
            "height": player_data.get("height"),
            "preferred_foot": player_data.get("preferredFoot"),
        }

        if stats_data:
            stats = stats_data.get("stats", {})
            result.update({
                "tournament": stats_data.get("tournament"),
                "season": stats_data.get("season"),
                "rating": stats.get("rating"),
                "goals": stats.get("goals"),
                "assists": stats.get("assists", stats.get("goalAssist")),
                "appearances": stats.get("appearances"),
                "minutes_played": stats.get("minutesPlayed"),
                "yellow_cards": stats.get("yellowCards"),
                "red_cards": stats.get("redCards"),
                "successful_dribbles": stats.get("successfulDribbles"),
                "total_passes": stats.get("totalPass"),
                "accurate_passes_pct": stats.get("accuratePassesPercentage"),
                "shots_on_target": stats.get("shotsOnTarget"),
                "tackles": stats.get("tackles"),
                "interceptions": stats.get("interceptions"),
                "clean_sheets": stats.get("cleanSheet"),
                "saves": stats.get("saves"),
            })

        # Fallback: si no hay rating de temporada, calcular de últimos partidos
        if not result.get("rating"):
            fallback_rating = self.get_player_rating_from_matches(player_id)
            if fallback_rating:
                result["rating"] = fallback_rating
                if not result.get("tournament"):
                    result["tournament"] = "Últimos partidos"

        return result


# Singleton
_client: Optional[SofascoreClient] = None


def get_sofascore_client() -> SofascoreClient:
    global _client
    if _client is None:
        _client = SofascoreClient()
    return _client
