#!/usr/bin/env python3
"""
Sofascore Local Sync — Runs from residential IP (Sofascore blocks datacenter IPs).
Connects directly to Neon PostgreSQL and syncs Sofascore ratings for all players.

Usage:
    python3 scripts/sync_sofascore_local.py
    
Requirements (install once):
    python3 -m pip install curl_cffi psycopg2-binary python-dotenv --break-system-packages
"""
print("🏠 Sofascore local sync starting...", flush=True)

import os
import sys
import time
from datetime import datetime
from pathlib import Path

# Load .env from project root
from dotenv import load_dotenv
project_root = Path(__file__).resolve().parent.parent
load_dotenv(project_root / ".env")

import psycopg2
from psycopg2.extras import execute_values
from curl_cffi import requests as cffi_requests

# --- Config ---
DATABASE_URL = os.getenv("DATABASE_URL", "")
FUTMONDO_EMAIL = os.getenv("FUTMONDO_EMAIL", "")
FUTMONDO_PASSWORD = os.getenv("FUTMONDO_PASSWORD", "")
CHAMPIONSHIP_ID = os.getenv("CHAMPIONSHIP_ID", "592416daa3a2dd871a7a9956")
BASE_URL = os.getenv("BASE_URL", "https://api.futmondo.com")

SOFASCORE_BASE = "https://api.sofascore.com/api/v1"
MIN_DELAY = 0.75  # 750ms between Sofascore requests
PAUSE_EVERY = 20  # Pause every N players
PAUSE_DURATION = 5  # Seconds to pause
BATCH_SIZE = 50  # DB write batch size

# Colors for terminal output
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
CYAN = "\033[96m"
RESET = "\033[0m"
DIM = "\033[2m"


def get_db_connection():
    """Connect directly to Neon PostgreSQL."""
    if not DATABASE_URL:
        print(f"{RED}❌ DATABASE_URL not set in .env{RESET}")
        sys.exit(1)
    conn = psycopg2.connect(DATABASE_URL)
    conn.autocommit = True
    return conn


def get_players_from_db(conn):
    """Get players from active championships (no Futmondo login needed)."""
    cursor = conn.cursor()
    cursor.execute("""
        SELECT DISTINCT p.name, p.real_team_id 
        FROM players p
        INNER JOIN player_championship_stats pcs ON pcs.player_id = p.player_id
        INNER JOIN user_championships uc ON uc.championship_id = pcs.championship_id
        WHERE p.name IS NOT NULL AND p.name != ''
        ORDER BY p.name
    """)
    players = [{"name": row[0], "teamId": row[1] or ""} for row in cursor.fetchall()]
    cursor.close()
    return players


class SofascoreLocal:
    """Minimal Sofascore client for local execution."""
    
    # LaLiga team map for team hints
    LALIGA_TEAMS = {
        "504e581e4d8bec9a670000c6": "Real Madrid", "504e581e4d8bec9a670000c7": "Barcelona",
        "504e581e4d8bec9a670000c8": "Atlético de Madrid", "504e581e4d8bec9a670000c9": "Athletic de Bilbao",
        "504e581e4d8bec9a670000ca": "Rayo Vallecano", "504e581e4d8bec9a670000cb": "Valencia",
        "504e581e4d8bec9a670000cc": "Betis", "504e581e4d8bec9a670000cd": "Getafe",
        "504e581e4d8bec9a670000ce": "Real Sociedad", "504e581e4d8bec9a670000cf": "Levante",
        "504e581e4d8bec9a670000d0": "Espanyol", "504e581e4d8bec9a670000d1": "Osasuna",
        "504e581e4d8bec9a670000d5": "Sevilla", "504e581e4d8bec9a670000d6": "Málaga",
        "504e581e4d8bec9a670000d8": "Deportivo de la Coruña", "504e581e4d8bec9a670000d9": "Celta de Vigo",
        "51b889b1e401a15f2c0000f0": "Elche", "51b890f5b986415a2c000012": "Villarreal",
        "52038563b8d07d930b00008a": "Alavés", "520e4ee4a776cc826b00004b": "Racing",
    }

    # Tournaments to exclude (national teams, cups)
    EXCLUDED_KEYWORDS = {'world cup', 'euro ', 'copa america', 'nations league', 'friendlies', 'olympic'}
    
    CURRENT_SEASON_KEYWORDS = ['26/27', '2026-2027', '2026/2027']
    PREVIOUS_SEASON_KEYWORDS = ['25/26', '2025-2026', '2025/2026']
    PRIORITY_KEYWORDS = ['laliga', 'la liga']

    def __init__(self):
        self.session = cffi_requests.Session(impersonate="chrome")
        self._last_request = 0

    def _throttle(self):
        elapsed = time.time() - self._last_request
        if elapsed < MIN_DELAY:
            time.sleep(MIN_DELAY - elapsed)
        self._last_request = time.time()

    def _get(self, endpoint):
        self._throttle()
        try:
            resp = self.session.get(f"{SOFASCORE_BASE}{endpoint}", timeout=10)
            if resp.status_code == 200:
                return resp.json()
            return None
        except Exception:
            return None

    def search_player(self, name, team_hint=None):
        self._throttle()
        try:
            resp = self.session.get(
                f"{SOFASCORE_BASE}/search/players",
                params={"q": name}, timeout=10
            )
            if resp.status_code != 200:
                return None
            
            data = resp.json()
            results = data.get("results", [])
            if not results:
                return None

            if team_hint:
                team_hint_lower = team_hint.lower()
                for r in results:
                    entity = r.get("entity", r)
                    entity_team = (entity.get("team", {}) or {}).get("name", "")
                    if entity_team and team_hint_lower in entity_team.lower():
                        return {"id": entity.get("id"), "name": entity.get("name"),
                                "team": entity_team}

            entity = results[0].get("entity", results[0])
            return {"id": entity.get("id"), "name": entity.get("name"),
                    "team": (entity.get("team", {}) or {}).get("name", "")}
        except Exception:
            return None

    def get_player_stats(self, player_id):
        """Get stats with priority: current LaLiga > current any > prev LaLiga > prev any."""
        data = self._get(f"/player/{player_id}/statistics/seasons")
        if not data:
            return None

        seasons = data.get("uniqueTournamentSeasons", [])
        candidates = []

        for ts in seasons:
            tournament = ts.get("uniqueTournament", {})
            tname = (tournament.get("name") or "").lower()
            if any(kw in tname for kw in self.EXCLUDED_KEYWORDS):
                continue

            for season in ts.get("seasons", [])[:2]:
                sname = (season.get("name") or "").lower()
                is_priority = any(kw in tname for kw in self.PRIORITY_KEYWORDS)
                is_current = any(kw in sname for kw in self.CURRENT_SEASON_KEYWORDS)
                is_previous = any(kw in sname for kw in self.PREVIOUS_SEASON_KEYWORDS)

                if is_priority and is_current: priority = 1
                elif is_current: priority = 2
                elif is_priority and is_previous: priority = 3
                elif is_previous: priority = 4
                else: priority = 5

                candidates.append((priority, tournament, season))

        candidates.sort(key=lambda x: x[0])

        for priority, tournament, season in candidates:
            stats = self._get(
                f"/player/{player_id}/unique-tournament/{tournament.get('id')}"
                f"/season/{season.get('id')}/statistics/overall"
            )
            if stats and stats.get("statistics"):
                stat_data = stats["statistics"]
                if stat_data.get("rating") or (stat_data.get("appearances") and stat_data["appearances"] >= 3):
                    return {
                        "tournament": tournament.get("name", ""),
                        "season": season.get("name", ""),
                        "stats": stat_data,
                    }
        return None

    def get_player_full_info(self, player_id):
        """Get profile + stats."""
        profile = self._get(f"/player/{player_id}")
        if not profile:
            return None

        p = profile.get("player", {})
        result = {
            "id": player_id,
            "name": p.get("name", ""),
            "slug": p.get("slug", ""),
            "sofascore_url": f"https://www.sofascore.com/football/player/{p.get('slug', '')}/{player_id}",
            "position": p.get("position", ""),
            "team": (p.get("team", {}) or {}).get("name"),
            "nationality": (p.get("country", {}) or {}).get("name"),
            "age": p.get("age"),
        }

        stats_data = self.get_player_stats(player_id)
        if stats_data:
            stats = stats_data.get("stats", {})
            result.update({
                "tournament": stats_data.get("tournament"),
                "season": stats_data.get("season"),
                "rating": stats.get("rating"),
                "goals": stats.get("goals"),
                "assists": stats.get("assists", stats.get("goalAssist")),
                "appearances": stats.get("appearances"),
                "matches_started": stats.get("matchesStarted"),
                "minutes_played": stats.get("minutesPlayed"),
                "yellow_cards": stats.get("yellowCards"),
                "red_cards": stats.get("redCards"),
                "successful_dribbles": stats.get("successfulDribbles"),
                "accurate_passes_pct": stats.get("accuratePassesPercentage"),
                "shots_on_target": stats.get("shotsOnTarget"),
                "tackles": stats.get("tackles"),
                "interceptions": stats.get("interceptions"),
                "clean_sheets": stats.get("cleanSheet"),
                "saves": stats.get("saves"),
            })

        return result


def write_batch(conn, rows):
    """Write a batch of Sofascore cache rows using UPSERT."""
    if not rows:
        return
    cursor = conn.cursor()
    execute_values(cursor, """
        INSERT INTO sofascore_cache 
        (player_name, sofascore_id, sofascore_name, team,
         rating, goals, assists, appearances, matches_started, minutes_played,
         yellow_cards, red_cards, tournament, season, position,
         nationality, age, successful_dribbles, accurate_passes_pct,
         shots_on_target, tackles, interceptions, clean_sheets, saves,
         sofascore_url, synced_at)
        VALUES %s
        ON CONFLICT (player_name) DO UPDATE SET
            sofascore_id = EXCLUDED.sofascore_id, sofascore_name = EXCLUDED.sofascore_name,
            team = EXCLUDED.team, rating = EXCLUDED.rating, goals = EXCLUDED.goals,
            assists = EXCLUDED.assists, appearances = EXCLUDED.appearances,
            matches_started_prev = CASE 
                WHEN sofascore_cache.season != EXCLUDED.season AND sofascore_cache.matches_started > 0 
                THEN sofascore_cache.matches_started 
                ELSE sofascore_cache.matches_started_prev 
            END,
            matches_started = EXCLUDED.matches_started, minutes_played = EXCLUDED.minutes_played,
            yellow_cards = EXCLUDED.yellow_cards, red_cards = EXCLUDED.red_cards,
            tournament = EXCLUDED.tournament, season = EXCLUDED.season,
            position = EXCLUDED.position, nationality = EXCLUDED.nationality,
            age = EXCLUDED.age, successful_dribbles = EXCLUDED.successful_dribbles,
            accurate_passes_pct = EXCLUDED.accurate_passes_pct,
            shots_on_target = EXCLUDED.shots_on_target, tackles = EXCLUDED.tackles,
            interceptions = EXCLUDED.interceptions, clean_sheets = EXCLUDED.clean_sheets,
            saves = EXCLUDED.saves, sofascore_url = EXCLUDED.sofascore_url,
            synced_at = EXCLUDED.synced_at
    """, rows, page_size=50)
    cursor.close()


def main():
    start_time = time.time()
    
    # Connect to DB
    print(f"\n{CYAN}📡 Connecting to Neon PostgreSQL...{RESET}", flush=True)
    conn = get_db_connection()
    print(f"{GREEN}✅ Connected{RESET}", flush=True)
    
    # Get players directly from DB (no Futmondo login needed)
    print(f"{CYAN}📋 Loading players from database...{RESET}", flush=True)
    all_players = get_players_from_db(conn)
    
    if not all_players:
        print(f"{RED}❌ No players found in database{RESET}")
        sys.exit(1)
    
    # Build unique player list with team hints
    players_to_sync = []
    seen = set()
    for p in all_players:
        name = p["name"]
        if name.lower() not in seen:
            team_hint = SofascoreLocal.LALIGA_TEAMS.get(p.get("teamId", ""), "")
            players_to_sync.append({"name": name, "team": team_hint})
            seen.add(name.lower())
    
    total = len(players_to_sync)
    print(f"{CYAN}⚽ Starting Sofascore sync for {total} players...{RESET}\n", flush=True)
    
    # Sync loop
    sofascore = SofascoreLocal()
    synced = 0
    errors = 0
    cache_rows = []
    now = datetime.now()
    
    for i, p in enumerate(players_to_sync, 1):
        name = p["name"]
        team_hint = p["team"]
        
        # Search player
        search_result = sofascore.search_player(name, team_hint=team_hint)
        if not search_result or not search_result.get("id"):
            print(f"  {DIM}[{i}/{total}]{RESET} {name} {RED}✗ not found{RESET}", flush=True)
            errors += 1
            continue
        
        # Get full info
        full_info = sofascore.get_player_full_info(search_result["id"])
        if not full_info:
            print(f"  {DIM}[{i}/{total}]{RESET} {name} {RED}✗ no stats{RESET}", flush=True)
            errors += 1
            continue
        
        rating = full_info.get("rating")
        tournament = full_info.get("tournament", "")
        season = full_info.get("season", "")
        matches_started = full_info.get("matches_started") or 0
        
        # Print live output
        rating_str = f"{rating:.2f}" if rating else "-.--"
        color = GREEN if rating and rating >= 7.0 else YELLOW if rating and rating >= 6.5 else RESET
        print(
            f"  {DIM}[{i}/{total}]{RESET} {name:<25} "
            f"{color}{rating_str}{RESET}  "
            f"{DIM}({matches_started} starts, {tournament} {season}){RESET}",
            flush=True
        )
        
        cache_rows.append((
            name,
            full_info.get("id"), full_info.get("name"), full_info.get("team"),
            rating, full_info.get("goals"), full_info.get("assists"),
            full_info.get("appearances"), matches_started,
            full_info.get("minutes_played"),
            full_info.get("yellow_cards"), full_info.get("red_cards"),
            tournament, season,
            full_info.get("position"), full_info.get("nationality"),
            full_info.get("age"), full_info.get("successful_dribbles"),
            full_info.get("accurate_passes_pct"), full_info.get("shots_on_target"),
            full_info.get("tackles"), full_info.get("interceptions"),
            full_info.get("clean_sheets"), full_info.get("saves"),
            full_info.get("sofascore_url", ""), now,
        ))
        synced += 1
        
        # Write in batches
        if len(cache_rows) >= BATCH_SIZE:
            write_batch(conn, cache_rows)
            cache_rows = []
        
        # Pause every N players
        if i % PAUSE_EVERY == 0 and i < total:
            print(f"  {DIM}  ... pausing {PAUSE_DURATION}s (rate limit){RESET}", flush=True)
            time.sleep(PAUSE_DURATION)
    
    # Write remaining
    if cache_rows:
        write_batch(conn, cache_rows)
    
    conn.close()
    
    # Summary
    duration = time.time() - start_time
    minutes = int(duration // 60)
    seconds = int(duration % 60)
    
    print(f"\n{'='*60}", flush=True)
    print(f"{GREEN}✅ Sofascore sync complete{RESET}", flush=True)
    print(f"   Synced: {synced}/{total} players", flush=True)
    print(f"   Errors: {errors}", flush=True)
    print(f"   Duration: {minutes}m {seconds}s", flush=True)
    print(f"{'='*60}\n", flush=True)


if __name__ == "__main__":
    main()
