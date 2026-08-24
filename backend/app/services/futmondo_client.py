#!/usr/bin/env python3
"""
Futmondo API Client - Core API communication module
"""

import requests
import json
import time
from typing import Dict, List, Optional
import logging
from app.core.config import BASE_URL, REQUEST_DELAY_SECONDS

logger = logging.getLogger(__name__)

class FutmondoClient:
    """Core Futmondo API client for authentication and data fetching"""
    
    def __init__(self, email: str, password: str):
        self.email = email
        self.password = password
        self.base_url = BASE_URL
        self.session = requests.Session()
        self.token = None
        self.user_id = None
        
        # Set default headers
        self.session.headers.update({
            'Accept': '*/*',
            'Accept-Language': 'es-ES,es;q=0.9',
            'Connection': 'keep-alive',
            'Content-Type': 'application/json; charset=utf-8',
            'Origin': 'https://app.futmondo.com',
            'Referer': 'https://app.futmondo.com/',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-site',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36',
            'sec-ch-ua': '"Chromium";v="140", "Not=A?Brand";v="24", "Google Chrome";v="140"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"macOS"'
        })
    
    def login(self) -> bool:
        """Login to Futmondo and get authentication token"""
        logger.info("Attempting to login to Futmondo...")
        logger.debug(f"Login email: {self.email}")
        logger.debug(f"Login base URL: {self.base_url}")
        
        if not self.email or not self.password:
            logger.error("Email or password not set. Please configure FUTMONDO_EMAIL and FUTMONDO_PASSWORD")
            return False
        
        # Check if using example credentials
        if "ejemplo.com" in self.email or self.email == "tu_email@ejemplo.com":
            logger.error("⚠️  Using example credentials! Please update .env file with your real Futmondo credentials")
            return False
        
        # Login format matching the working curl example
        login_data = {
            "header": {
                "token": "null",  # Must be string "null", not None
                "userid": ""
            },
            "query": {
                "mail": self.email,
                "pwd": self.password
            },
            "answer": {}
        }
        
        try:
            login_url = f"{self.base_url}/5/login/with_mail"
            logger.info(f"Login URL: {login_url}")
            logger.debug(f"Login data (email only): {json.dumps({k: (v if k != 'query' else {**v, 'pwd': '***'}) for k, v in login_data.items()}, indent=2)}")
            
            response = self.session.post(
                login_url,
                json=login_data,
                timeout=10
            )
            
            logger.info(f"Response status: {response.status_code}")
            response.raise_for_status()
            
            data = response.json()
            
            # Log full response for debugging
            logger.info(f"Login response status: {response.status_code}")
            logger.debug(f"Login response: {json.dumps(data, indent=2)}")
            
            answer = data.get("answer", {})
            
            # Check for success: answer.code should be "api.general.ok"
            if answer.get("code") == "api.general.ok":
                # Check for mobile login success
                mobile = answer.get("mobile", {})
                if mobile.get("code") == "login.mobile.ok":
                    if "token" in mobile and "userid" in mobile:
                        self.token = mobile["token"]
                        self.user_id = mobile["userid"]
                        logger.info("✅ Login successful!")
                        logger.debug(f"Token: {self.token[:20]}...")
                        logger.debug(f"User ID: {self.user_id}")
                        return True
                    else:
                        logger.error("Login response missing token or userid")
                        return False
                else:
                    logger.error(f"Mobile login failed: {mobile.get('code', 'Unknown')}")
                    return False
            
            # Check for error (alternative error format)
            elif answer.get("error"):
                error_code = answer.get('code', 'Unknown error')
                error_message = answer.get('message', '')
                logger.error(f"Login failed: {error_code}")
                if error_message:
                    logger.error(f"Error message: {error_message}")
                logger.error(f"Full error response: {json.dumps(answer, indent=2)}")
                
                # Provide helpful error messages
                if "not_found" in str(error_code).lower():
                    logger.error("⚠️  User not found or invalid credentials. Please verify:")
                    logger.error("   1. Email is correct")
                    logger.error("   2. Password is correct")
                    logger.error("   3. Account exists and is active")
                
                return False
            
            # Unknown response format
            else:
                logger.error(f"Unknown login response format: {json.dumps(data, indent=2)}")
                return False
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Login request failed: {e}")
            return False
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse login response: {e}")
            return False
    
    def _make_request(self, endpoint: str, data: Dict) -> Optional[Dict]:
        """Make authenticated API request"""
        if not self.token or not self.user_id:
            logger.error("Not authenticated. Please login first.")
            return None
        
        try:
            response = self.session.post(f"{self.base_url}{endpoint}", json=data, timeout=15)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.Timeout:
            logger.error(f"API request timed out: {endpoint}")
            return None
        except requests.exceptions.RequestException as e:
            logger.error(f"API request failed: {e}")
            return None
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse API response: {e}")
            return None
    
    def get_championship_players(self, championship_id: str) -> Optional[Dict]:
        """Fetch all championship players with their clause information
        
        Args:
            championship_id: The championship ID
            
        Returns:
            Dict with 'players' list containing player data with clause info, or None if error
        """
        logger.debug(f"Fetching championship players for {championship_id}...")
        
        request_data = {
            "header": {
                "token": self.token,
                "userid": self.user_id
            },
            "query": {
                "championshipId": championship_id
            },
            "answer": {}
        }
        
        response = self._make_request("/5/league/championshipplayers", request_data)
        if response:
            answer = response.get("answer", {})
            # The API returns a dict with 'players' key
            if isinstance(answer, dict):
                players = answer.get("players", [])
                logger.info(f"Retrieved {len(players)} players")
                return answer
            # Fallback: if it's a list, wrap it
            if isinstance(answer, list):
                logger.info(f"Retrieved {len(answer)} players (list format)")
                return {"players": answer}
        return None
    
    def get_player_summary(self, championship_id: str, player_id: str, user_team_id: str) -> Optional[Dict]:
        """Get detailed player information including transaction history"""
        request_data = {
            "header": {
                "token": self.token,
                "userid": self.user_id
            },
            "query": {
                "championshipId": championship_id,
                "userteamId": user_team_id,
                "playerId": player_id
            },
            "answer": {}
        }
        
        response = self._make_request("/1/player/summary", request_data)
        if response:
            return response.get("answer", {})
        return None
    
    def get_matchday_standings(self, championship_id: str, matchday: Optional[int] = None) -> Optional[Dict]:
        """Fetch matchday standings/rankings"""
        logger.info(f"Fetching matchday standings for matchday {matchday if matchday else 'current'}...")
        
        request_data = {
            "header": {
                "token": self.token,
                "userid": self.user_id
            },
            "query": {
                "championshipId": championship_id
            },
            "answer": {}
        }
        
        if matchday:
            request_data["query"]["matchday"] = matchday
        
        response = self._make_request("/2/championship/teams", request_data)
        if response:
            return response.get("answer", {})
        return None
    
    def get_matchday_history(self, championship_id: str, max_matchdays: int = 38) -> Optional[List[Dict]]:
        """Fetch historical matchday standings for all matchdays"""
        logger.info(f"Fetching matchday history for up to {max_matchdays} matchdays...")
        
        matchday_history = []
        for matchday in range(1, max_matchdays + 1):
            standings = self.get_matchday_standings(championship_id, matchday)
            if standings:
                matchday_history.append({
                    "matchday": matchday,
                    "standings": standings
                })
                time.sleep(REQUEST_DELAY_SECONDS)
            else:
                # If we can't get data for this matchday, we've probably reached the end
                break
        
        logger.info(f"Retrieved data for {len(matchday_history)} matchdays")
        return matchday_history if matchday_history else None
    
    def get_nightmare_team(self, championship_id: str, matchday: Optional[int] = None) -> Optional[Dict]:
        """Fetch the nightmare team (worst performing team) for a championship"""
        logger.info(f"Fetching nightmare team for matchday {matchday if matchday else 'current'}...")
        
        request_data = {
            "header": {
                "token": self.token,
                "userid": self.user_id
            },
            "query": {
                "championshipId": championship_id
            },
            "answer": {}
        }
        
        if matchday:
            request_data["query"]["matchday"] = matchday
        
        response = self._make_request("/1/userteam/nightmareteam", request_data)
        if response:
            return response.get("answer", {})
        return None
    
    def get_dream_team(self, championship_id: str, round_id: Optional[str] = None, matchday: Optional[int] = None) -> Optional[Dict]:
        """Fetch the dream team (best performing team) for a championship
        
        Args:
            championship_id: Championship ID
            round_id: Round ID (string, preferred method)
            matchday: Matchday number (int, legacy support)
        """
        if round_id:
            logger.info(f"Fetching dream team for round {round_id}...")
        else:
            logger.info(f"Fetching dream team for matchday {matchday if matchday else 'current'}...")
        
        request_data = {
            "header": {
                "token": self.token,
                "userid": self.user_id
            },
            "query": {
                "championshipId": championship_id,
                "type": "dreamteam"
            },
            "answer": {}
        }
        
        # Use round_id if provided (preferred), otherwise use matchday
        if round_id:
            request_data["query"]["round"] = round_id
        elif matchday:
            request_data["query"]["matchday"] = matchday
        
        response = self._make_request("/1/userteam/dreamteam", request_data)
        if response:
            return response.get("answer", {})
        return None
    
    def get_match_list(self, championship_id: str, matchday: Optional[int] = None) -> Optional[Dict]:
        """Fetch the list of matches for a championship"""
        logger.info(f"Fetching match list for matchday {matchday if matchday else 'all'}...")
        
        request_data = {
            "header": {
                "token": self.token,
                "userid": self.user_id
            },
            "query": {
                "championshipId": championship_id
            },
            "answer": {}
        }
        
        if matchday:
            request_data["query"]["matchday"] = matchday
        
        response = self._make_request("/1/match/list", request_data)
        if response:
            return response.get("answer", {})
        return None

    def get_round_matches(self, championship_id: str, round_id: str, userteam_id: str) -> Optional[Dict]:
        """Get matches for a specific round (to check if all are finished)."""
        request_data = {
            "header": {"token": self.token, "userid": self.user_id},
            "query": {
                "championshipId": championship_id,
                "userteamId": userteam_id,
                "roundId": round_id,
            },
            "answer": {}
        }
        response = self._make_request("/1/match/list", request_data)
        if response:
            return response.get("answer", {})
        return None

    def get_round_lineup(self, championship_id: str, round_id: str, userteam_id: str) -> Optional[List]:
        """Get a team's lineup for a specific round (historical snapshot)."""
        request_data = {
            "header": {"token": self.token, "userid": self.user_id},
            "query": {
                "championshipId": championship_id,
                "round": round_id,
                "userteamId": userteam_id,
            },
            "answer": {}
        }
        response = self._make_request("/1/userteam/roundlineup", request_data)
        if response:
            answer = response.get("answer", {})
            if isinstance(answer, dict):
                return answer.get("players", [])
        return None

    def get_userteam_rounds(self, championship_id: str, user_team_id: str) -> Optional[List]:
        """Fetch rounds/matchday information for a specific user team
        
        Returns a list of rounds, each containing:
        - id: round ID
        - number: matchday number
        - status: 'closed' or 'running'
        - points: points for that matchday
        - negative: boolean
        """
        logger.debug(f"Fetching rounds for user team {user_team_id}...")
        
        request_data = {
            "header": {
                "token": self.token,
                "userid": self.user_id
            },
            "query": {
                "championshipId": championship_id,
                "userteamId": user_team_id
            },
            "answer": {}
        }
        
        response = self._make_request("/1/userteam/rounds", request_data)
        if response:
            answer = response.get("answer", [])
            # Answer can be a list directly or a dict with a list inside
            if isinstance(answer, list):
                return answer
            elif isinstance(answer, dict):
                # Try to find a list in the dict
                for key in answer:
                    if isinstance(answer[key], list):
                        return answer[key]
                return []
        return None
    
    def get_userteam_roster(self, championship_id: str, user_team_id: str) -> Optional[List]:
        """Fetch roster/team lineup for a specific user team
        
        Returns a list of players in the team with detailed information:
        - id, name, role, team, value, points
        - photo: URL of player photo
        - formation position
        - individual statistics
        """
        logger.debug(f"Fetching roster for user team {user_team_id}...")
        
        request_data = {
            "header": {
                "token": self.token,
                "userid": self.user_id
            },
            "query": {
                "championshipId": championship_id,
                "userteamId": user_team_id
            },
            "answer": {}
        }
        
        response = self._make_request("/1/userteam/roster", request_data)
        if response:
            answer = response.get("answer", {})
            # Answer might be a dict with players array or directly a list
            if isinstance(answer, dict):
                players = answer.get("players", answer.get("roster", []))
                if isinstance(players, list):
                    return players
            elif isinstance(answer, list):
                return answer
        return None
    
    def get_user_roundlineup(self, championship_id: str, round_id: str, userteam_id: str) -> Optional[Dict]:
        """Fetch user team lineup for a specific round
        
        Args:
            championship_id: Championship ID
            round_id: Round ID (string)
            userteam_id: User team ID
            
        Returns:
            Dict with lineup data including players array, or None if error
        """
        logger.debug(f"Fetching round lineup for user team {userteam_id} in round {round_id}...")
        
        request_data = {
            "header": {
                "token": self.token,
                "userid": self.user_id
            },
            "query": {
                "championshipId": championship_id,
                "round": round_id,
                "userteamId": userteam_id
            },
            "answer": {}
        }
        
        response = self._make_request("/1/userteam/roundlineup", request_data)
        if response:
            return response.get("answer", {})
        return None
    
    def get_round_ranking(
        self,
        championship_id: str,
        round_number: Optional[int] = None,
        round_id: Optional[str] = None,
        userteam_id: Optional[str] = None
    ) -> Optional[Dict]:
        """Fetch ranking for a specific round/matchday.

        Args:
            championship_id: Futmondo championship ID.
            round_number: Numerical matchday (1..38). Optional if round_id provided.
            round_id: Futmondo round identifier (preferred).
            userteam_id: Optional user team ID to mimic app requests.

        Returns:
            Dict containing ranking data (same shape as Futmondo API) or None.
        """
        identifier = round_id or round_number
        logger.debug(f"Fetching ranking for round identifier {identifier}...")

        request_data = {
            "header": {
                "token": self.token,
                "userid": self.user_id
            },
            "query": {
                "championshipId": championship_id
            },
            "answer": {}
        }

        if round_id:
            # Futmondo app sends both keys; replicate for compatibility.
            request_data["query"]["roundId"] = round_id
            request_data["query"]["roundNumber"] = round_id
        if round_number is not None:
            request_data["query"]["round"] = round_number
        if userteam_id:
            request_data["query"]["userteamId"] = userteam_id

        response = self._make_request("/1/ranking/round", request_data)
        if not response:
            return None

        answer = response.get("answer")
        if isinstance(answer, dict):
            return answer
        if isinstance(answer, list):
            return {"ranking": answer}
        return None
    
    def get_market_players(self, championship_id: str) -> Optional[List]:
        """Fetch players available in the transfer market
        
        Returns a list of players available for purchase/sale with:
        - Player data
        - Market price
        - Market statistics
        - Availability status
        """
        logger.debug("Fetching market players...")
        
        request_data = {
            "header": {
                "token": self.token,
                "userid": self.user_id
            },
            "query": {
                "championshipId": championship_id
            },
            "answer": {}
        }
        
        response = self._make_request("/1/market/players", request_data)
        if response:
            answer = response.get("answer", {})
            # Answer might be a dict with players array or directly a list
            if isinstance(answer, dict):
                players = answer.get("players", answer.get("market", []))
                if isinstance(players, list):
                    return players
            elif isinstance(answer, list):
                return answer
        return None
    
    def get_pressroom_news(self, championship_id: str, from_id: Optional[str] = None) -> Optional[Dict]:
        """Fetch pressroom/news updates for the championship with pagination support
        
        Args:
            championship_id: The championship ID
            from_id: Optional transaction ID to paginate from (use last transaction _id)
        
        Returns:
            Dict with 'news' list containing transactions, or None if error
        """
        logger.debug("Fetching pressroom news...")
        
        request_data = {
            "header": {
                "token": self.token,
                "userid": self.user_id
            },
            "query": {
                "championshipId": championship_id,
                "from": from_id if from_id else ""  # Empty string for first page
            },
            "answer": {}
        }
        
        response = self._make_request("/1/locker/pressroom", request_data)
        if response:
            answer = response.get("answer", {})
            # Return the full answer dict (contains 'news' array and potentially 'isAdmin')
            if isinstance(answer, dict):
                return answer
            elif isinstance(answer, list):
                # If answer is directly a list, wrap it
                return {"news": answer}
        return None
    
    def get_player_fullprofile(self, player_id: str) -> Optional[Dict]:
        """Fetch full player profile including historical prices.
        
        Args:
            player_id: Futmondo player ID
        
        Returns:
            Dict with player info and 'prices' array (date + classic/social values), or None
        """
        request_data = {
            "header": {
                "token": self.token,
                "userid": self.user_id
            },
            "query": {
                "playerId": player_id
            },
            "answer": {}
        }
        
        response = self._make_request("/1/player/fullprofile", request_data)
        if response:
            return response.get("answer", {})
        return None

    def get_locker_news(self, championship_id: str, from_id: Optional[str] = None) -> Optional[Dict]:
        """Fetch locker news (punishments and bonuses) with pagination support
        
        Args:
            championship_id: The championship ID
            from_id: Optional news ID to paginate from (use last news _id)
        
        Returns:
            Dict with 'news' or 'data' list containing punishments/bonuses, or None if error
        """
        logger.debug("Fetching locker news...")
        
        request_data = {
            "header": {
                "token": self.token,
                "userid": self.user_id
            },
            "query": {
                "championshipId": championship_id,
                "from": from_id if from_id else ""  # Empty string for first page
            },
            "answer": {}
        }
        
        response = self._make_request("/2/locker/news", request_data)
        if response:
            answer = response.get("answer", {})
            # The response might have 'news' or 'data' array
            if isinstance(answer, dict):
                return answer
            elif isinstance(answer, list):
                return {"news": answer}
        return None
    
    def get_league_list(self) -> Optional[List[Dict]]:
        """Fetch list of all leagues with their rounds
        
        Returns a list of leagues, each containing:
        - _id: league ID
        - name: league name
        - rounds: list of rounds with _id and status
        """
        logger.debug("Fetching league list...")
        
        request_data = {
            "header": {
                "token": self.token,
                "userid": self.user_id
            },
            "query": "",
            "answer": {}
        }
        
        response = self._make_request("/2/league/list", request_data)
        if response:
            answer = response.get("answer", [])
            if isinstance(answer, list):
                return answer
        return None
    
    def is_authenticated(self) -> bool:
        """Check if client is authenticated"""
        return self.token is not None and self.user_id is not None

