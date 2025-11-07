"""
Service to generate funny press news for matchdays using OpenAI
"""

import logging
from typing import Dict, Optional
from openai import OpenAI
from app.core.config import OPENAI_API_KEY, OPENAI_MODEL
from app.services.data_manager_v2 import DataManagerV2

logger = logging.getLogger(__name__)


class NewsGenerator:
    """Generate funny press news for matchdays using OpenAI"""
    
    def __init__(self):
        self.data_manager = DataManagerV2()
        self.client = None
        if OPENAI_API_KEY:
            self.client = OpenAI(api_key=OPENAI_API_KEY)
        else:
            logger.warning("⚠️ OpenAI API key not configured. News generation will be disabled.")
    
    def generate_matchday_news(self, championship_id: str, matchday: int) -> Dict[str, str]:
        """Generate funny press news for a specific matchday"""
        if not self.client:
            return {
                "error": "OpenAI API key not configured",
                "news": None
            }
        
        # Get matchday data
        matchday_data = self.data_manager.get_matchday_data_for_news(championship_id, matchday)
        
        # Build prompt for OpenAI
        prompt = self._build_prompt(matchday_data)
        
        try:
            response = self.client.chat.completions.create(
                model=OPENAI_MODEL,
                messages=[
                    {
                        "role": "system",
                        "content": "Eres un periodista deportivo chistoso y creativo que escribe notas de prensa sobre un campeonato de fútbol fantasy. Escribe de manera divertida, con humor, mencionando situaciones específicas, sorpresas, decepciones y momentos clave. Sé creativo y entretenido."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.8,
                max_tokens=1000
            )
            
            news_text = response.choices[0].message.content
            
            return {
                "matchday": matchday,
                "news": news_text,
                "generated_at": matchday_data.get("matchday")
            }
        except Exception as e:
            logger.error(f"Error generating news with OpenAI: {e}")
            return {
                "error": str(e),
                "news": None
            }
    
    def _build_prompt(self, matchday_data: Dict) -> str:
        """Build the prompt for OpenAI based on matchday data"""
        matchday = matchday_data.get("matchday", 0)
        current_standings = matchday_data.get("current_standings", [])
        previous_standings = matchday_data.get("previous_standings", {})
        best_players = matchday_data.get("best_players", [])
        top_players = matchday_data.get("top_players", [])
        
        prompt = f"""Escribe una nota de prensa divertida y chistosa sobre la Jornada {matchday} de este campeonato de fútbol fantasy.

**SITUACIÓN GENERAL:**
"""
        
        # Add standings
        prompt += "\n**CLASIFICACIÓN (después de la jornada):**\n"
        for idx, team in enumerate(current_standings[:10], 1):  # Top 10
            team_name = team.get("team_name", "Equipo")
            username = team.get("username", "")
            position = team.get("position", 0)
            points = team.get("points", 0)
            points_matchday = team.get("points_this_matchday", 0)
            
            # Get previous position if available
            team_id = team.get("team_id")
            prev_info = previous_standings.get(team_id, {})
            prev_position = prev_info.get("position", position)
            position_change = prev_position - position  # Positive = moved up
            
            change_str = ""
            if position_change > 0:
                change_str = f" (subió {position_change} posición{'es' if position_change > 1 else ''})"
            elif position_change < 0:
                change_str = f" (bajó {abs(position_change)} posición{'es' if abs(position_change) > 1 else ''})"
            
            prompt += f"{position}. {team_name} ({username}) - {points} puntos (+{points_matchday} esta jornada){change_str}\n"
        
        # Add position changes
        prompt += "\n**CAMBIOS DE POSICIÓN:**\n"
        notable_changes = []
        for team in current_standings:
            team_id = team.get("team_id")
            team_name = team.get("team_name", "Equipo")
            username = team.get("username", "")
            position = team.get("position", 0)
            prev_info = previous_standings.get(team_id, {})
            prev_position = prev_info.get("position", position)
            position_change = prev_position - position
            
            if abs(position_change) >= 2:  # Notable changes (2+ positions)
                if position_change > 0:
                    notable_changes.append(f"- {team_name} ({username}) subió {position_change} posiciones (de {prev_position} a {position})")
                elif position_change < 0:
                    notable_changes.append(f"- {team_name} ({username}) bajó {abs(position_change)} posiciones (de {prev_position} a {position})")
        
        if notable_changes:
            prompt += "\n".join(notable_changes[:5]) + "\n"
        else:
            prompt += "No hubo cambios significativos en las posiciones.\n"
        
        # Add best players
        if best_players:
            prompt += "\n**MEJORES JUGADORES DE CADA EQUIPO (esta jornada):**\n"
            for player in best_players[:5]:
                player_name = player.get("player_name", "Jugador")
                team_name = player.get("team_name", "Equipo")
                points = player.get("player_points", 0)
                prompt += f"- {player_name} ({team_name}): {points} puntos\n"
        
        # Add top players
        if top_players:
            prompt += "\n**TOP JUGADORES DE LA JORNADA:**\n"
            for idx, player in enumerate(top_players[:5], 1):
                player_name = player.get("player_name", "Jugador")
                team_name = player.get("team_name", "Equipo")
                points = player.get("points", 0)
                prompt += f"{idx}. {player_name} ({team_name}): {points} puntos\n"
        
        # Add interesting facts
        prompt += "\n**HECHOS INTERESANTES:**\n"
        # Find surprise performances (players with low average that scored high)
        for player in top_players:
            player_name = player.get("player_name", "")
            points = player.get("points", 0)
            team_name = player.get("team_name", "")
            if points >= 10:  # High scoring player
                prompt += f"- {player_name} tuvo una gran jornada con {points} puntos, salvando parcialmente a {team_name}\n"
        
        # Find teams that struggled
        low_scoring_teams = [t for t in current_standings if t.get("points_this_matchday", 0) < 20]
        if low_scoring_teams:
            prompt += f"- Varios equipos tuvieron jornadas complicadas con pocos puntos\n"
        
        # Find teams that were close to overtaking but didn't
        for i, team in enumerate(current_standings):
            if i > 0:  # Skip first place
                team_id = team.get("team_id")
                team_name = team.get("team_name", "")
                username = team.get("username", "")
                position = team.get("position", 0)
                points = team.get("points", 0)
                prev_info = previous_standings.get(team_id, {})
                prev_position = prev_info.get("position", position)
                
                # Check if team was close to overtaking the team above
                if prev_position > position:  # Team moved up
                    # Check points difference with team above
                    if i < len(current_standings):
                        team_above = current_standings[i-1]
                        team_above_id = team_above.get("team_id")
                        team_above_name = team_above.get("team_name", "")
                        team_above_points = team_above.get("points", 0)
                        points_diff = team_above_points - points
                        
                        if 0 < points_diff <= 15:  # Close to overtaking
                            prompt += f"- {team_name} ({username}) estuvo cerca de adelantar a {team_above_name} pero la diferencia de {points_diff} puntos se mantuvo\n"
        
        prompt += """
**INSTRUCCIONES:**
Escribe una nota de prensa divertida, chistosa y entretenida que comente:
- Los cambios de posición más significativos (menciona específicamente si parecía que un equipo iba a adelantar a otro pero finalmente no pudo debido a los puntos que obtuvieron sus jugadores)
- Los jugadores que funcionaban muy bien en jornadas anteriores pero que esta jornada no rindieron lo esperado
- Las sorpresas de jugadores con pocos puntos acumulados que tuvieron una gran jornada y salvaron la jornada para sus equipos
- La situación general del campeonato y cómo ha evolucionado
- Haz referencias específicas y directas a nombres de equipos, usuarios y jugadores
- Usa un tono desenfadado, humorístico y entretenido
- Comenta sobre las decepciones, las sorpresas y los momentos clave de la jornada

Escribe aproximadamente 400-600 palabras. Empieza con un título llamativo y divertido. Sé creativo y específico."""
        
        return prompt

