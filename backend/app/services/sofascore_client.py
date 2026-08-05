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
        self._min_delay = 1.0  # Mínimo 1 segundo entre requests

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

    def search_player(self, name: str) -> Optional[Dict]:
        """Busca un jugador por nombre. Devuelve el primer resultado relevante."""
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

            # Primer resultado
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
        """Obtiene estadísticas del jugador (prioriza liga de club sobre selecciones)."""
        data = self._get(f"/player/{player_id}/statistics/seasons")
        if not data:
            return None

        seasons = data.get("uniqueTournamentSeasons", [])
        if not seasons:
            return None

        # Torneos a excluir (selecciones/copas internacionales)
        EXCLUDED_KEYWORDS = {'world cup', 'euro ', 'copa america', 'nations league', 'friendlies', 'olympic'}
        
        # Torneos prioritarios (ligas españolas primero)
        PRIORITY_KEYWORDS = ['laliga', 'la liga', 'liga 2']
        
        # Clasificar candidatos
        priority_candidates = []
        normal_candidates = []
        
        for tournament_season in seasons:
            tournament = tournament_season.get("uniqueTournament", {})
            tournament_name = (tournament.get("name") or "").lower()
            
            # Excluir torneos de selecciones
            if any(kw in tournament_name for kw in EXCLUDED_KEYWORDS):
                continue
            
            seasons_list = tournament_season.get("seasons", [])
            if seasons_list:
                entry = (tournament, seasons_list[0])
                if any(kw in tournament_name for kw in PRIORITY_KEYWORDS):
                    priority_candidates.append(entry)
                else:
                    normal_candidates.append(entry)

        # Ordenar: primero prioritarios, luego normales
        candidates = priority_candidates + normal_candidates

        # Si no hay candidatos de club, usar todos
        if not candidates:
            for tournament_season in seasons:
                tournament = tournament_season.get("uniqueTournament", {})
                seasons_list = tournament_season.get("seasons", [])
                if seasons_list:
                    candidates.append((tournament, seasons_list[0]))

        # Probar cada candidato hasta encontrar stats
        for tournament, latest_season in candidates:
            season_id = latest_season.get("id")
            tournament_id = tournament.get("id")

            stats = self._get(
                f"/player/{player_id}/unique-tournament/{tournament_id}/season/{season_id}/statistics/overall"
            )
            if stats and stats.get("statistics"):
                return {
                    "tournament": tournament.get("name", ""),
                    "season": latest_season.get("name", ""),
                    "stats": stats["statistics"],
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
        """Calcula rating medio a partir de los últimos partidos jugados."""
        data = self._get(f"/player/{player_id}/events/last/0")
        if not data:
            return None

        stats_map = data.get("statisticsMap", {})
        events = data.get("events", [])

        ratings = []
        for event in events[:20]:  # Máximo 20 partidos
            event_id = str(event.get("id"))
            stats = stats_map.get(event_id, {})
            rating = stats.get("rating")
            if rating:
                ratings.append(rating)

        if ratings:
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
