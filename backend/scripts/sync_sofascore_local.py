#!/usr/bin/env python3
"""
Sofascore Local Sync — Runs from residential IP (Sofascore blocks datacenter IPs).

STRATEGY (v2 — batch by league):
    Sofascore's website loads its "Player statistics" table via a single paginated
    endpoint that returns ~100 players per request WITH their season stats (rating,
    goals, assists, appearances, matchesStarted, minutes, cards, ...).

        GET /api/v1/unique-tournament/{utId}/season/{seasonId}/statistics
            ?limit=100&offset=0&order=-rating&group=all

    Instead of ~4-10 requests PER PLAYER (search + profile + seasons + N×overall),
    which meant ~1500-3000 requests total and got the IP banned, we now download the
    whole LaLiga table for the current + previous season in ~12-20 requests, and match
    players locally by normalised name. This is a ~99% reduction in request volume.

    Players that don't match LaLiga (transfers from other leagues, loans) fall back to
    the old per-player flow — but only for that small remainder.

Usage:
    python3 scripts/sync_sofascore_local.py            # full batch sync
    python3 scripts/sync_sofascore_local.py --verify   # only probe the endpoint (use to test when IP recovers)
    python3 scripts/sync_sofascore_local.py --no-fallback   # skip per-player fallback

Requirements (install once):
    python3 -m pip install curl_cffi psycopg2-binary python-dotenv --break-system-packages
"""
print("🏠 Sofascore local sync starting...", flush=True)

import os
import sys
import time
import random
import unicodedata
from datetime import datetime
from pathlib import Path

# Load .env from project root
from dotenv import load_dotenv
project_root = Path(__file__).resolve().parent.parent.parent
load_dotenv(project_root / ".env")

import psycopg2
from psycopg2.extras import execute_values
from curl_cffi import requests as cffi_requests

# --- Config ---
DATABASE_URL = os.getenv("DATABASE_URL", "")

SOFASCORE_BASE = "https://api.sofascore.com/api/v1"

# LaLiga unique-tournament id on Sofascore (stable). LaLiga 2 (Hypermotion) is 54.
LALIGA_UT_ID = 8
LALIGA2_UT_ID = 54

# How many players Sofascore returns per statistics page.
PAGE_LIMIT = 100

# Request pacing. With ~12-20 total requests we can afford to look human.
MIN_DELAY = 3.0
MAX_DELAY = 7.0
MAX_RETRIES = 2
RETRY_WAIT = 90  # base backoff on 403 (grows per attempt)

BATCH_SIZE = 50  # DB write batch size

# --- Incremental league learning ---
# When the per-player fallback resolves a player, we record the league its
# chosen rating came from. Next runs fetch that league in batch instead of
# hitting the per-player endpoints again.
#
# Threshold: fetching a league in batch costs ~6 requests; resolving a player
# via fallback costs ~4. So batching a league only pays off when >= 2 of our
# players need it (2*4 = 8 fallback reqs > 6 batch reqs). Leagues with a single
# player stay on the cheaper fallback path.
LEAGUE_BATCH_MIN_PLAYERS = 2
# Drop learned leagues not seen in this many days (player left that league).
LEAGUE_MAX_AGE_DAYS = 30
# Leagues always fetched in batch regardless of learning.
FIXED_LEAGUES = [(LALIGA_UT_ID, "LaLiga"), (LALIGA2_UT_ID, "LaLiga 2")]

# Season name keywords for classification / matching.
CURRENT_SEASON_KEYWORDS = ["26/27", "2026-2027", "2026/2027"]
PREVIOUS_SEASON_KEYWORDS = ["25/26", "2025-2026", "2025/2026"]

# Colors for terminal output
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
CYAN = "\033[96m"
RESET = "\033[0m"
DIM = "\033[2m"


# ----------------------------------------------------------------------------
# Name normalisation for local matching
# ----------------------------------------------------------------------------
def normalize_name(name: str) -> str:
    """Lowercase, strip accents and punctuation for robust name matching."""
    if not name:
        return ""
    # Decompose accents and drop combining marks
    nfkd = unicodedata.normalize("NFKD", name)
    no_accents = "".join(c for c in nfkd if not unicodedata.combining(c))
    # Keep alnum + spaces only
    cleaned = "".join(c if c.isalnum() or c.isspace() else " " for c in no_accents)
    return " ".join(cleaned.lower().split())


def match_keys(name: str) -> list:
    """Generate matching keys for a name, from most to least specific.

    Futmondo often stores short names while Sofascore uses full names. The short
    name may be either the surname OR the first name:
      - 'Oyarzabal'  -> 'Mikel Oyarzabal'   (surname)
      - 'Alfon'      -> 'Alfon González'     (first name)
      - 'Jonny'      -> 'Jonny Otto'         (first name)
    So we key by: full name, last-two tokens, last token (surname) and first
    token (first name). Ordered from most to least specific to prefer precise
    matches and only fall back to single-token (more ambiguous) keys last.
    """
    nm = normalize_name(name)
    if not nm:
        return []
    toks = nm.split()
    keys = [nm]
    if len(toks) >= 2:
        keys.append(" ".join(toks[-2:]))
    if toks:
        keys.append(toks[-1])          # surname (last token)
    if len(toks) >= 2:
        keys.append(toks[0])           # first name (first token)
    # Dedup preserving order
    seen = set()
    out = []
    for k in keys:
        if k not in seen:
            seen.add(k)
            out.append(k)
    return out


# ----------------------------------------------------------------------------
# Database
# ----------------------------------------------------------------------------
def get_db_connection():
    if not DATABASE_URL:
        print(f"{RED}❌ DATABASE_URL not set in .env{RESET}")
        sys.exit(1)
    conn = psycopg2.connect(DATABASE_URL)
    conn.autocommit = True
    return conn


def get_players_from_db(conn):
    """Get all players from the players table (name + real_team_id)."""
    cursor = conn.cursor()
    cursor.execute("""
        SELECT DISTINCT name, real_team_id
        FROM players
        WHERE name IS NOT NULL AND name != ''
        ORDER BY name
    """)
    players = [{"name": row[0], "teamId": row[1] or ""} for row in cursor.fetchall()]
    cursor.close()
    return players


def ensure_leagues_table(conn):
    """Create the learned-leagues table if it doesn't exist."""
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sofascore_leagues (
            unique_tournament_id INTEGER PRIMARY KEY,
            name TEXT,
            player_count INTEGER DEFAULT 0,
            last_seen_at TIMESTAMP DEFAULT NOW()
        )
    """)
    cursor.close()


def get_learned_leagues(conn):
    """Return learned leagues eligible for batch fetching (player_count >= threshold).

    Fixed leagues (LaLiga/LaLiga2) are excluded so we don't fetch them twice.
    """
    cursor = conn.cursor()
    fixed_ids = tuple(ut for ut, _ in FIXED_LEAGUES)
    cursor.execute(
        """
        SELECT unique_tournament_id, name
        FROM sofascore_leagues
        WHERE player_count >= %s
          AND unique_tournament_id != ALL(%s)
        ORDER BY player_count DESC
        """,
        (LEAGUE_BATCH_MIN_PLAYERS, list(fixed_ids)),
    )
    leagues = [(row[0], row[1] or f"League {row[0]}") for row in cursor.fetchall()]
    cursor.close()
    return leagues


def upsert_learned_leagues(conn, league_counts: dict, league_names: dict):
    """Record leagues discovered during fallback.

    league_counts: {ut_id: number_of_players_resolved_from_it_this_run}
    league_names:  {ut_id: league_name}
    Sets player_count to this run's count (authoritative) and refreshes last_seen_at.
    """
    if not league_counts:
        return
    cursor = conn.cursor()
    for ut_id, count in league_counts.items():
        # Never learn the fixed leagues (already always batched).
        if ut_id in {ut for ut, _ in FIXED_LEAGUES}:
            continue
        cursor.execute(
            """
            INSERT INTO sofascore_leagues (unique_tournament_id, name, player_count, last_seen_at)
            VALUES (%s, %s, %s, NOW())
            ON CONFLICT (unique_tournament_id) DO UPDATE SET
                name = EXCLUDED.name,
                player_count = EXCLUDED.player_count,
                last_seen_at = NOW()
            """,
            (ut_id, league_names.get(ut_id), count),
        )
    cursor.close()


def purge_stale_leagues(conn):
    """Remove learned leagues not seen within LEAGUE_MAX_AGE_DAYS."""
    cursor = conn.cursor()
    cursor.execute(
        "DELETE FROM sofascore_leagues "
        "WHERE last_seen_at < NOW() - make_interval(days => %s)",
        (int(LEAGUE_MAX_AGE_DAYS),),
    )
    cursor.close()


def purge_transfer_shadows(conn, run_ts):
    """Remove stale rows left behind when a player changes club.

    The cache UNIQUE is (player_name, team), so when a player transfers (e.g.
    Betis -> Real Madrid) this run inserts a fresh row for the new team while the
    old-team row lingers as a shadow. We delete any row NOT written in this run
    (synced_at < run_ts) whose sofascore_id matches a row that WAS written this
    run. Using sofascore_id (not name) preserves legitimate namesakes on
    different teams (e.g. two different 'Gueye' players have distinct ids).

    Returns number of shadow rows deleted.
    """
    cursor = conn.cursor()
    cursor.execute(
        """
        DELETE FROM sofascore_cache old
        WHERE old.synced_at < %s
          AND old.sofascore_id IS NOT NULL
          AND EXISTS (
            SELECT 1 FROM sofascore_cache fresh
            WHERE fresh.sofascore_id = old.sofascore_id
              AND fresh.synced_at >= %s
              AND fresh.team IS DISTINCT FROM old.team
          )
        """,
        (run_ts, run_ts),
    )
    deleted = cursor.rowcount if cursor.rowcount is not None else 0
    cursor.close()
    return deleted


# ----------------------------------------------------------------------------
# Sofascore client
# ----------------------------------------------------------------------------
class SofascoreLocal:
    """Minimal Sofascore client. Batch-first, per-player fallback."""

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

    EXCLUDED_KEYWORDS = {'world cup', 'euro ', 'copa america', 'nations league', 'friendlies', 'olympic'}
    PRIORITY_KEYWORDS = ['laliga', 'la liga']

    # Statistics fields we request from the aggregated endpoint.
    STAT_FIELDS = (
        "goals,assists,rating,appearances,matchesStarted,minutesPlayed,"
        "yellowCards,redCards,successfulDribbles,accuratePassesPercentage,"
        "shotsOnTarget,tackles,interceptions,cleanSheet,saves"
    )

    def __init__(self):
        self.session = cffi_requests.Session(impersonate="chrome")
        self._last_request = 0

    def _throttle(self):
        """Randomised pacing to avoid a robotic, detectable request pattern."""
        elapsed = time.time() - self._last_request
        wait = random.uniform(MIN_DELAY, MAX_DELAY)
        if elapsed < wait:
            time.sleep(wait - elapsed)
        self._last_request = time.time()

    def _get(self, endpoint, params=None):
        self._throttle()
        for attempt in range(MAX_RETRIES + 1):
            try:
                resp = self.session.get(
                    f"{SOFASCORE_BASE}{endpoint}", params=params, timeout=15
                )
                if resp.status_code == 200:
                    return resp.json()
                if resp.status_code == 403:
                    if attempt < MAX_RETRIES:
                        wait = RETRY_WAIT * (attempt + 1)
                        print(f"  {YELLOW}⏳ 403 (IP throttled). Waiting {wait}s...{RESET}", flush=True)
                        time.sleep(wait)
                        continue
                    # IP is banned — signal caller to stop hammering.
                    raise SofascoreBanned(endpoint)
                if resp.status_code == 404:
                    return None
                return None
            except SofascoreBanned:
                raise
            except Exception:
                return None
        return None

    # --- Season discovery -------------------------------------------------
    def get_season_ids(self, ut_id):
        """Return list of (season_id, season_name, priority) for current+previous seasons.
        priority: 1 = current, 2 = previous.
        """
        data = self._get(f"/unique-tournament/{ut_id}/seasons")
        if not data:
            return []
        result = []
        for season in data.get("seasons", []):
            sname = (season.get("name") or "").lower()
            if any(kw in sname for kw in CURRENT_SEASON_KEYWORDS):
                result.append((season.get("id"), season.get("name"), 1))
            elif any(kw in sname for kw in PREVIOUS_SEASON_KEYWORDS):
                result.append((season.get("id"), season.get("name"), 2))
        return result

    # --- Batch statistics -------------------------------------------------
    def get_league_statistics(self, ut_id, season_id):
        """Download all players' season statistics for a league/season, paginated.

        Returns a list of dicts (one per player) with the fields we store.
        Uses the same endpoint the Sofascore website uses for its stats table.
        """
        players = []
        offset = 0
        while True:
            data = self._get(
                f"/unique-tournament/{ut_id}/season/{season_id}/statistics",
                params={
                    "limit": PAGE_LIMIT,
                    "offset": offset,
                    "order": "-rating",
                    "group": "all",
                    "fields": self.STAT_FIELDS,
                },
            )
            if not data:
                break
            rows = data.get("results", [])
            if not rows:
                break
            players.extend(rows)
            # Pagination: Sofascore returns 'pages' or we stop when a short page arrives.
            pages = data.get("pages")
            if pages is not None:
                if offset // PAGE_LIMIT + 1 >= pages:
                    break
            elif len(rows) < PAGE_LIMIT:
                break
            offset += PAGE_LIMIT
        return players

    # --- Per-player fallback ---------------------------------------------
    def search_player(self, name, team_hint=None):
        data = self._get("/search/players", params={"q": name})
        if not data:
            return None
        results = data.get("results", [])
        if not results:
            return None

        # Keep only football players. Sofascore search returns all sports, so
        # e.g. "Hugo González" can return an NBA (Boston Celtics) player first.
        def is_football(r):
            entity = r.get("entity", r)
            sport = ((entity.get("team", {}) or {}).get("sport", {}) or {}).get("name") \
                or entity.get("sport")
            # Accept when sport is Football or unknown (some entities omit it),
            # but reject explicit non-football sports.
            return sport is None or str(sport).lower() == "football"

        results = [r for r in results if is_football(r)]
        if not results:
            return None

        if team_hint:
            th = team_hint.lower()
            for r in results:
                entity = r.get("entity", r)
                entity_team = (entity.get("team", {}) or {}).get("name", "")
                if entity_team and th in entity_team.lower():
                    return {"id": entity.get("id"), "name": entity.get("name"),
                            "slug": entity.get("slug"), "team": entity_team}
        entity = results[0].get("entity", results[0])
        return {"id": entity.get("id"), "name": entity.get("name"),
                "slug": entity.get("slug"),
                "team": (entity.get("team", {}) or {}).get("name", "")}

    def get_player_full_info(self, player_id):
        """Legacy per-player path. Limited to 2 season candidates to cap requests."""
        profile = self._get(f"/player/{player_id}")
        if not profile:
            return None
        p = profile.get("player", {})
        result = {
            "id": player_id,
            "name": p.get("name", ""),
            "slug": p.get("slug", ""),
            "sofascore_url": f"https://www.sofascore.com/football/player/{p.get('slug', '')}/{player_id}",
            "team": (p.get("team", {}) or {}).get("name"),
        }

        seasons_data = self._get(f"/player/{player_id}/statistics/seasons")
        candidates = []
        if seasons_data:
            for ts in seasons_data.get("uniqueTournamentSeasons", []):
                tournament = ts.get("uniqueTournament", {})
                tname = (tournament.get("name") or "").lower()
                if any(kw in tname for kw in self.EXCLUDED_KEYWORDS):
                    continue
                for season in ts.get("seasons", [])[:2]:
                    sname = (season.get("name") or "").lower()
                    is_priority = any(kw in tname for kw in self.PRIORITY_KEYWORDS)
                    is_current = any(kw in sname for kw in CURRENT_SEASON_KEYWORDS)
                    is_previous = any(kw in sname for kw in PREVIOUS_SEASON_KEYWORDS)
                    if is_priority and is_current: priority = 1
                    elif is_current: priority = 2
                    elif is_priority and is_previous: priority = 3
                    elif is_previous: priority = 4
                    else: priority = 5
                    candidates.append((priority, tournament, season))
        candidates.sort(key=lambda x: x[0])

        # Cap: only try the top 2 candidates to avoid request amplification.
        for priority, tournament, season in candidates[:2]:
            stats = self._get(
                f"/player/{player_id}/unique-tournament/{tournament.get('id')}"
                f"/season/{season.get('id')}/statistics/overall"
            )
            if stats and stats.get("statistics"):
                sd = stats["statistics"]
                if sd.get("rating") or (sd.get("appearances") and sd["appearances"] >= 3):
                    result.update(_map_stats(sd))
                    result["tournament"] = tournament.get("name", "")
                    result["season"] = season.get("name", "")
                    # League of the chosen rating, for incremental learning.
                    result["league_ut_id"] = tournament.get("id")
                    result["league_name"] = tournament.get("name", "")
                    break
        return result


class SofascoreBanned(Exception):
    """Raised when Sofascore returns 403 after retries (IP banned)."""
    pass


def _map_stats(sd: dict) -> dict:
    """Map a Sofascore 'statistics' dict to our storage fields."""
    return {
        "rating": sd.get("rating"),
        "goals": sd.get("goals"),
        "assists": sd.get("assists", sd.get("goalAssist")),
        "appearances": sd.get("appearances"),
        "matches_started": sd.get("matchesStarted"),
        "minutes_played": sd.get("minutesPlayed"),
        "yellow_cards": sd.get("yellowCards"),
        "red_cards": sd.get("redCards"),
        "successful_dribbles": sd.get("successfulDribbles"),
        "accurate_passes_pct": sd.get("accuratePassesPercentage"),
        "shots_on_target": sd.get("shotsOnTarget"),
        "tackles": sd.get("tackles"),
        "interceptions": sd.get("interceptions"),
        "clean_sheets": sd.get("cleanSheet"),
        "saves": sd.get("saves"),
    }


# ----------------------------------------------------------------------------
# DB write
# ----------------------------------------------------------------------------
def write_batch(conn, rows):
    """UPSERT a batch of Sofascore cache rows. Reconnects on dropped connection."""
    if not rows:
        return conn
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        cursor.close()
    except Exception:
        print(f"  {YELLOW}🔄 Reconnecting to database...{RESET}", flush=True)
        try:
            conn.close()
        except Exception:
            pass
        conn = get_db_connection()

    cursor = conn.cursor()
    execute_values(cursor, """
        INSERT INTO sofascore_cache
        (player_name, sofascore_id, sofascore_name, team,
         rating, goals, assists, appearances, matches_started, minutes_played,
         yellow_cards, red_cards, tournament, season,
         successful_dribbles, accurate_passes_pct,
         shots_on_target, tackles, interceptions, clean_sheets, saves,
         sofascore_url, synced_at)
        VALUES %s
        ON CONFLICT (player_name, team) DO UPDATE SET
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
            successful_dribbles = EXCLUDED.successful_dribbles,
            accurate_passes_pct = EXCLUDED.accurate_passes_pct,
            shots_on_target = EXCLUDED.shots_on_target, tackles = EXCLUDED.tackles,
            interceptions = EXCLUDED.interceptions, clean_sheets = EXCLUDED.clean_sheets,
            saves = EXCLUDED.saves, sofascore_url = EXCLUDED.sofascore_url,
            synced_at = EXCLUDED.synced_at
    """, rows, page_size=50)
    cursor.close()
    return conn


def build_row(local_name, info, now):
    """Build a DB row tuple from a resolved player info dict."""
    return (
        local_name,
        info.get("id"), info.get("name"), info.get("team"),
        info.get("rating"), info.get("goals"), info.get("assists"),
        info.get("appearances"), info.get("matches_started") or 0,
        info.get("minutes_played"),
        info.get("yellow_cards"), info.get("red_cards"),
        info.get("tournament"), info.get("season"),
        info.get("successful_dribbles"),
        info.get("accurate_passes_pct"), info.get("shots_on_target"),
        info.get("tackles"), info.get("interceptions"),
        info.get("clean_sheets"), info.get("saves"),
        info.get("sofascore_url", ""), now,
    )


# ----------------------------------------------------------------------------
# Batch statistics → player info
# ----------------------------------------------------------------------------
def stat_row_to_info(row, tournament_name, season_name):
    """Convert one row from the league statistics endpoint to our info dict."""
    player = row.get("player", {}) or {}
    team = row.get("team", {}) or {}
    pid = player.get("id")
    slug = player.get("slug", "")
    info = {
        "id": pid,
        "name": player.get("name", ""),
        "slug": slug,
        "sofascore_url": f"https://www.sofascore.com/football/player/{slug}/{pid}" if pid else "",
        "team": team.get("name"),
        "tournament": tournament_name,
        "season": season_name,
    }
    # The statistics endpoint returns stat fields at the row root.
    info.update(_map_stats(row))
    return info


# ----------------------------------------------------------------------------
# Verify mode
# ----------------------------------------------------------------------------
def verify_endpoint():
    """Probe the batch endpoint and print a small sample. Use when IP recovers."""
    print(f"\n{CYAN}🔎 Verifying Sofascore batch endpoint...{RESET}", flush=True)
    client = SofascoreLocal()
    try:
        seasons = client.get_season_ids(LALIGA_UT_ID)
    except SofascoreBanned:
        print(f"{RED}❌ 403 — IP is currently banned. Try again from a different IP.{RESET}")
        return False
    if not seasons:
        print(f"{RED}❌ Could not resolve LaLiga seasons (empty response).{RESET}")
        return False
    print(f"{GREEN}✅ Seasons resolved:{RESET} {seasons}", flush=True)

    sid, sname, _ = seasons[0]
    try:
        stats = client.get_league_statistics(LALIGA_UT_ID, sid)
    except SofascoreBanned:
        print(f"{RED}❌ 403 on statistics — IP banned.{RESET}")
        return False
    if not stats:
        print(f"{RED}❌ Statistics endpoint returned no rows.{RESET}")
        return False
    print(f"{GREEN}✅ Got {len(stats)} players for {sname}.{RESET}", flush=True)
    sample = stats[0]
    info = stat_row_to_info(sample, "LaLiga", sname)
    print(f"{DIM}Sample:{RESET} {info.get('name')} | rating={info.get('rating')} "
          f"| starts={info.get('matches_started')} | team={info.get('team')} | url={info.get('sofascore_url')}",
          flush=True)
    return True


# ----------------------------------------------------------------------------
# Main
# ----------------------------------------------------------------------------
def main():
    args = sys.argv[1:]
    if "--verify" in args:
        ok = verify_endpoint()
        sys.exit(0 if ok else 1)

    do_fallback = "--no-fallback" not in args
    start_time = time.time()

    print(f"\n{CYAN}📡 Connecting to Neon PostgreSQL...{RESET}", flush=True)
    conn = get_db_connection()
    print(f"{GREEN}✅ Connected{RESET}", flush=True)

    ensure_leagues_table(conn)
    learned_leagues = get_learned_leagues(conn)
    if learned_leagues:
        print(f"{CYAN}🧠 Learned leagues to batch: "
              f"{', '.join(n for _, n in learned_leagues)}{RESET}", flush=True)

    print(f"{CYAN}📋 Loading players from database...{RESET}", flush=True)
    all_players = get_players_from_db(conn)
    if not all_players:
        print(f"{RED}❌ No players found in database{RESET}")
        sys.exit(1)

    # Build unique local player list with team hint + normalised name index.
    local_players = []
    seen = set()
    for p in all_players:
        name = p["name"]
        team_id = p.get("teamId", "")
        key = f"{name.lower()}|{team_id}"
        if key not in seen:
            team_hint = SofascoreLocal.LALIGA_TEAMS.get(team_id, "")
            local_players.append({"name": name, "team": team_hint,
                                  "norm": normalize_name(name)})
            seen.add(key)

    total = len(local_players)

    print(f"{CYAN}⚽ {total} local players. Fetching LaLiga statistics (batch)...{RESET}\n", flush=True)

    client = SofascoreLocal()
    now = datetime.now()
    cache_rows = []
    synced = 0

    # --- Phase 1: batch by league ---
    # Download every league/season table first, then build an inverted index
    # keyed by match_keys() so short Futmondo names map to full Sofascore names.
    # Each Sofascore player keeps its highest-priority appearance
    # (current LaLiga > current LaLiga2 > previous seasons), so daily-changing
    # ratings come from the current season when available.
    sofa_index = {}  # key -> list of (priority, info)
    try:
        league_seasons = []
        # Fixed leagues (weight 0) always first; learned leagues (weight 1) after.
        batch_leagues = [(ut, name, 0) for ut, name in FIXED_LEAGUES] + \
                        [(ut, name, 1) for ut, name in learned_leagues]
        for ut_id, ut_label, league_weight in batch_leagues:
            seasons = client.get_season_ids(ut_id)
            if not seasons:
                print(f"  {YELLOW}⚠ No seasons resolved for {ut_label}{RESET}", flush=True)
                continue
            for sid, sname, season_prio in seasons:
                # season_prio: current(1) before prev(2); league_weight orders leagues.
                league_seasons.append((season_prio, league_weight, ut_id, ut_label, sid, sname))

        # Fetch in priority order: current LaLiga, current LaLiga2, prev LaLiga, prev LaLiga2
        for season_prio, league_weight, ut_id, ut_label, sid, sname in sorted(
            league_seasons, key=lambda x: (x[0], x[1])
        ):
            rows = client.get_league_statistics(ut_id, sid)
            print(f"  {DIM}{ut_label} {sname}: {len(rows)} players{RESET}", flush=True)
            priority = season_prio * 10 + league_weight
            for row in rows:
                info = stat_row_to_info(row, ut_label, sname)
                for k in match_keys(info.get("name", "")):
                    sofa_index.setdefault(k, []).append((priority, info))
    except SofascoreBanned:
        print(f"{RED}❌ Sofascore returned 403 (IP banned). Stopping batch phase.{RESET}", flush=True)
        conn.close()
        _summary(start_time, synced, total, 0, banned=True)
        sys.exit(2)

    # Match each local player against the index.
    matched_names = set()
    for lp in local_players:
        chosen_info = None
        for k in match_keys(lp["name"]):
            candidates = sofa_index.get(k)
            if not candidates:
                continue
            # Prefer team match, then lowest priority number (best season/league).
            best = None
            for prio, info in sorted(candidates, key=lambda x: x[0]):
                if lp["team"] and info.get("team"):
                    tl = info["team"].lower()
                    ml = lp["team"].lower()
                    if ml in tl or tl in ml:
                        best = info
                        break
                if best is None:
                    best = info  # first (best-priority) as fallback
            chosen_info = best
            if chosen_info:
                break
        if chosen_info:
            matched_names.add(lp["name"])
            cache_rows.append(build_row(lp["name"], chosen_info, now))
            synced += 1
            if len(cache_rows) >= BATCH_SIZE:
                conn = write_batch(conn, cache_rows)
                cache_rows = []

    if cache_rows:
        conn = write_batch(conn, cache_rows)
        cache_rows = []

    matched = len(matched_names)
    unmatched = [lp for lp in local_players if lp["name"] not in matched_names]
    print(f"\n{GREEN}✅ Batch phase: matched {matched}/{total}. "
          f"{len(unmatched)} unmatched (non-LaLiga / name mismatch).{RESET}\n", flush=True)

    # --- Phase 2: per-player fallback for unmatched only ---
    errors = 0
    league_counts = {}   # ut_id -> players resolved from it this run
    league_names = {}    # ut_id -> league name
    if do_fallback and unmatched:
        # Optional cap (env FALLBACK_LIMIT) to bound a single run's fallback work.
        fb_limit = os.getenv("FALLBACK_LIMIT")
        if fb_limit and fb_limit.isdigit():
            unmatched = unmatched[: int(fb_limit)]
        print(f"{CYAN}🔁 Fallback per-player for {len(unmatched)} unmatched...{RESET}", flush=True)
        try:
            for i, lp in enumerate(unmatched, 1):
                name = lp["name"]
                search = client.search_player(name, team_hint=lp["team"])
                if not search or not search.get("id"):
                    print(f"  {DIM}[{i}/{len(unmatched)}]{RESET} {name} {RED}✗ not found{RESET}", flush=True)
                    errors += 1
                    continue
                info = client.get_player_full_info(search["id"])
                if not info or not info.get("rating"):
                    print(f"  {DIM}[{i}/{len(unmatched)}]{RESET} {name} {RED}✗ no stats{RESET}", flush=True)
                    errors += 1
                    continue
                rating = info.get("rating")
                print(f"  {DIM}[{i}/{len(unmatched)}]{RESET} {name:<25} "
                      f"{rating:.2f} {DIM}({info.get('tournament','')} {info.get('season','')}){RESET}",
                      flush=True)
                # Learn the league this rating came from (skip fixed leagues).
                lut = info.get("league_ut_id")
                if lut and lut not in {ut for ut, _ in FIXED_LEAGUES}:
                    league_counts[lut] = league_counts.get(lut, 0) + 1
                    league_names[lut] = info.get("league_name") or league_names.get(lut)
                cache_rows.append(build_row(name, info, now))
                synced += 1
                if len(cache_rows) >= BATCH_SIZE:
                    conn = write_batch(conn, cache_rows)
                    cache_rows = []
        except SofascoreBanned:
            print(f"{RED}❌ 403 during fallback (IP banned). Persisting and exiting.{RESET}", flush=True)
            conn = write_batch(conn, cache_rows)
            # Persist whatever leagues we learned before the ban.
            upsert_learned_leagues(conn, league_counts, league_names)
            conn.close()
            _summary(start_time, synced, total, errors, banned=True)
            sys.exit(2)

        if cache_rows:
            conn = write_batch(conn, cache_rows)

        # Record learned leagues for next runs, then drop stale ones.
        upsert_learned_leagues(conn, league_counts, league_names)
        purge_stale_leagues(conn)
        newly_batchable = [ut for ut, c in league_counts.items()
                           if c >= LEAGUE_BATCH_MIN_PLAYERS]
        if newly_batchable:
            names = ", ".join(league_names.get(ut, str(ut)) for ut in newly_batchable)
            print(f"{CYAN}🧠 Leagues learned for next run (>= "
                  f"{LEAGUE_BATCH_MIN_PLAYERS} players): {names}{RESET}", flush=True)

    # Remove shadow rows left by players who changed club (mismo id, distinto team).
    try:
        shadows = purge_transfer_shadows(conn, now)
        if shadows:
            print(f"{CYAN}🧹 Removed {shadows} stale transfer-shadow rows{RESET}", flush=True)
    except Exception as shadow_err:
        print(f"{YELLOW}⚠ Shadow cleanup failed: {shadow_err}{RESET}", flush=True)

    conn.close()
    _summary(start_time, synced, total, errors)


def _summary(start_time, synced, total, errors, banned=False):
    duration = time.time() - start_time
    minutes = int(duration // 60)
    seconds = int(duration % 60)
    print(f"\n{'='*60}", flush=True)
    if banned:
        print(f"{YELLOW}⚠ Sofascore sync stopped early (IP banned){RESET}", flush=True)
    else:
        print(f"{GREEN}✅ Sofascore sync complete{RESET}", flush=True)
    print(f"   Synced: {synced}/{total} players", flush=True)
    print(f"   Errors: {errors}", flush=True)
    print(f"   Duration: {minutes}m {seconds}s", flush=True)
    print(f"{'='*60}\n", flush=True)


if __name__ == "__main__":
    main()
