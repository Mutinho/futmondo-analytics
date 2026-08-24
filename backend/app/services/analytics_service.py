"""Analytics service for advanced championship insights."""

import math
import statistics
from collections import defaultdict
from typing import Dict, List, Optional

from app.services.data_manager_v2 import DataManagerV2


class AnalyticsService:
    """Provides high-level analytics derived from historical Futmondo data."""

    def __init__(self):
        self.dm = DataManagerV2()
        self._team_cache: Dict[str, Dict[str, Dict]] = {}
        self._player_cache: Dict[str, Dict] = {}

    def _safe_team_info(self, team_id: str) -> Dict:
        if not team_id:
            return {}
        if hasattr(self.dm, "get_team_by_id"):
            try:
                return self.dm.get_team_by_id(team_id) or {}
            except Exception:
                return {}
        return {}

    LALIGA_TEAMS = {
        "504e581e4d8bec9a670000c6": "Real Madrid", "504e581e4d8bec9a670000c7": "Barcelona",
        "504e581e4d8bec9a670000c8": "Atlético de Madrid", "504e581e4d8bec9a670000c9": "Athletic de Bilbao",
        "504e581e4d8bec9a670000ca": "Rayo Vallecano", "504e581e4d8bec9a670000cb": "Valencia",
        "504e581e4d8bec9a670000cc": "Betis", "504e581e4d8bec9a670000cd": "Getafe",
        "504e581e4d8bec9a670000ce": "Real Sociedad", "504e581e4d8bec9a670000cf": "Levante",
        "504e581e4d8bec9a670000d0": "Espanyol", "504e581e4d8bec9a670000d1": "Osasuna",
        "504e581e4d8bec9a670000d5": "Sevilla", "504e581e4d8bec9a670000d6": "Málaga",
        "504e581e4d8bec9a670000d8": "Deportivo", "504e581e4d8bec9a670000d9": "Celta de Vigo",
        "51b889b1e401a15f2c0000f0": "Elche", "51b890f5b986415a2c000012": "Villarreal",
        "52038563b8d07d930b00008a": "Alavés", "520e4ee4a776cc826b00004b": "Racing",
    }

    def _resolve_real_team_name(self, team_id: str) -> str:
        return self.LALIGA_TEAMS.get(team_id, "")

    def _safe_player_info(self, player_id: str) -> Dict:
        if not player_id:
            return {}
        if hasattr(self.dm, "get_player_by_id"):
            try:
                if player_id in self._player_cache:
                    return self._player_cache[player_id]
                info = self.dm.get_player_by_id(player_id) or {}
                if info:
                    self._player_cache[player_id] = info
                return info
            except Exception:
                return {}
        return {}

    def _build_team_lookup(self, championship_id: str) -> Dict[str, Dict]:
        if championship_id in self._team_cache:
            return self._team_cache[championship_id]

        lookup = {
            "by_team": {},
            "by_user": {},
            "by_name": {}
        }

        try:
            users = self.dm.get_all_users_with_points(championship_id)
        except Exception:
            users = []

        for entry in users:
            team_id = entry.get("team_id")
            user_id = entry.get("user_id")
            team_name = entry.get("team_name")
            username = entry.get("username")

            info = {
                "team_id": team_id,
                "user_id": user_id,
                "team_name": team_name,
                "username": username
            }

            if team_id:
                lookup["by_team"][team_id] = info
            if user_id:
                lookup["by_user"][user_id] = info
            for name in (team_name, username):
                if name:
                    lookup["by_name"][name.strip().lower()] = info

        self._team_cache[championship_id] = lookup
        return lookup

    def _resolve_team(self, championship_id: str, identifier: Optional[str], fallback_name: Optional[str] = None) -> Dict:
        if not identifier and not fallback_name:
            return {}

        lookup = self._build_team_lookup(championship_id)
        info = None

        if identifier:
            info = lookup["by_team"].get(identifier) or lookup["by_user"].get(identifier)

        if not info and fallback_name:
            info = lookup["by_name"].get(fallback_name.strip().lower())

        if not info and identifier:
            info = self._safe_team_info(identifier)
            if info:
                lookup["by_team"][identifier] = info

        return info or {
            "team_id": identifier,
            "team_name": fallback_name or identifier,
            "user_id": None,
            "username": fallback_name or identifier
        }

    # ------------------------------------------------------------------
    # Championship analytics
    # ------------------------------------------------------------------

    def get_championship_trends(self, championship_id: str, window: Optional[int] = None) -> Dict:
        history = self.dm.get_team_standings_history(championship_id, window=window)
        latest_matchday = self.dm.get_latest_matchday(championship_id)

        trends: Dict[str, Dict] = {}
        for entry in history:
            team_id = entry["team_id"]
            team_info = self._safe_team_info(team_id)
            team_name = team_info.get("team_name", team_id)

            matchday = entry.get("matchday")
            total_points = entry.get("points")
            if total_points is None:
                total_points = 0
            points_this_matchday = entry.get("points_this_matchday")
            if points_this_matchday is None:
                points_this_matchday = 0
            position_value = entry.get("position")
            if position_value is None:
                position_value = 0
            team_value = entry.get("team_value")

            team_record = trends.setdefault(team_id, {
                "team_id": team_id,
                "team_name": team_name,
                "history": [],
                "total_points": 0,
                "positions": []
            })

            team_record["history"].append({
                "matchday": matchday,
                "points": total_points,
                "points_this_matchday": points_this_matchday,
                "position": position_value,
                "team_value": team_value,
            })
            team_record["positions"].append(position_value)
            team_record["total_points"] = max(team_record["total_points"], total_points)

        all_matchdays = set()

        for record in trends.values():
            record["history"].sort(key=lambda h: (h["matchday"] if h["matchday"] is not None else 0))
            positions = record.pop("positions", [])
            if positions:
                start_position = positions[0] if positions[0] is not None else 0
                end_position = positions[-1] if positions[-1] is not None else 0
                record["position_delta"] = end_position - start_position
            history_points = [h["points_this_matchday"] for h in record["history"] if h["points_this_matchday"] is not None]
            record["average_points"] = statistics.mean(history_points) if history_points else 0

            # compute moving trend slope using last values
            if len(history_points) >= 2:
                diffs = [b - a for a, b in zip(history_points[:-1], history_points[1:])]
                record["momentum"] = statistics.mean(diffs) if diffs else 0
            else:
                record["momentum"] = 0

            all_matchdays.update(h.get("matchday") for h in record["history"] if h.get("matchday") is not None)

        if all_matchdays:
            min_matchday = min(all_matchdays)
            if min_matchday and min_matchday > 1:
                for record in trends.values():
                    existing = {h.get("matchday") for h in record["history"]}
                    for md in range(1, min_matchday):
                        if md not in existing:
                            record["history"].insert(0, {
                                "matchday": md,
                                "points": 0,
                                "points_this_matchday": 0,
                                "position": None,
                                "team_value": None
                            })
                    record["history"].sort(key=lambda h: (h["matchday"] if h["matchday"] is not None else 0))

        return {
            "championship_id": championship_id,
            "latest_matchday": latest_matchday,
            "teams": sorted(trends.values(), key=lambda x: x["total_points"], reverse=True)
        }

    def get_championship_custom_classification(
        self,
        championship_id: str,
        window: Optional[int] = None,
        exclude_matchdays: Optional[List[int]] = None
    ) -> Dict:
        history = self.dm.get_team_standings_history(championship_id)
        latest_matchday = self.dm.get_latest_matchday(championship_id)

        if not history:
            return {
                "championship_id": championship_id,
                "latest_matchday": latest_matchday,
                "window": window,
                "excluded_matchdays": [],
                "available_matchdays": [],
                "included_matchdays": [],
                "classification": []
            }

        all_matchdays = sorted({entry["matchday"] for entry in history if entry.get("matchday") is not None})
        if not all_matchdays:
            return {
                "championship_id": championship_id,
                "latest_matchday": latest_matchday,
                "window": window,
                "excluded_matchdays": [],
                "available_matchdays": [],
                "included_matchdays": [],
                "classification": []
            }

        if window and latest_matchday:
            min_matchday = max(latest_matchday - window + 1, all_matchdays[0])
        else:
            min_matchday = all_matchdays[0]

        eligible_matchdays = [md for md in all_matchdays if md >= min_matchday]
        excluded_set = set()
        if exclude_matchdays:
            excluded_set = {int(md) for md in exclude_matchdays if md is not None}

        included_matchdays = [md for md in eligible_matchdays if md not in excluded_set]

        classification_map: Dict[str, Dict] = {}
        for entry in history:
            matchday = entry.get("matchday")
            if matchday is None or matchday < min_matchday or matchday not in included_matchdays:
                continue

            team_id = entry["team_id"]
            team_info = self._resolve_team(championship_id, team_id)
            points_this_matchday = entry.get("points_this_matchday")
            if points_this_matchday is None:
                points_this_matchday = 0

            record = classification_map.setdefault(team_id, {
                "team_id": team_info.get("team_id") or team_id,
                "team_name": team_info.get("team_name") or team_id,
                "user_id": team_info.get("user_id"),
                "username": team_info.get("username"),
                "points_total": 0.0,
                "points_values": [],
                "positions": [],
                "matchdays": []
            })

            record["points_total"] += points_this_matchday
            record["points_values"].append(points_this_matchday)
            record["positions"].append(entry.get("position"))
            record["matchdays"].append({
                "matchday": matchday,
                "points": points_this_matchday,
                "position": entry.get("position"),
                "team_value": entry.get("team_value")
            })

        classification: List[Dict] = []
        for record in classification_map.values():
            record["matchdays"].sort(key=lambda item: item["matchday"])
            points_series = record["points_values"]
            matches_played = len(points_series)
            avg_points = statistics.mean(points_series) if points_series else 0
            max_points = max(points_series) if points_series else 0
            min_points = min(points_series) if points_series else 0
            volatility = statistics.pstdev(points_series) if len(points_series) > 1 else 0
            trend = 0
            if len(points_series) >= 2:
                trend = points_series[-1] - points_series[-2]
            elif points_series:
                trend = points_series[-1]

            classification.append({
                "team_id": record["team_id"],
                "team_name": record["team_name"],
                "user_id": record["user_id"],
                "username": record["username"],
                "matches_count": matches_played,
                "total_points": round(record["points_total"], 2),
                "average_points": round(avg_points, 2),
                "max_points": max_points,
                "min_points": min_points,
                "volatility": round(volatility, 3),
                "trend": round(trend, 2),
                "points_by_matchday": {entry["matchday"]: entry["points"] for entry in record["matchdays"]},
                "matchdays": record["matchdays"],
                "last_matchday": record["matchdays"][-1]["matchday"] if record["matchdays"] else None
            })

        classification.sort(
            key=lambda item: (
                item["total_points"],
                item["average_points"],
                item["max_points"],
                -(item["volatility"] or 0)
            ),
            reverse=True
        )

        for idx, entry in enumerate(classification, start=1):
            entry["rank"] = idx

        return {
            "championship_id": championship_id,
            "latest_matchday": latest_matchday,
            "window": window,
            "excluded_matchdays": sorted(excluded_set),
            "available_matchdays": eligible_matchdays,
            "included_matchdays": included_matchdays,
            "classification": classification
        }

    def get_championship_heatmap(self, championship_id: str) -> Dict:
        history = self.dm.get_team_standings_history(championship_id)
        heatmap: Dict[int, Dict[str, float]] = defaultdict(dict)

        for entry in history:
            team_id = entry["team_id"]
            heatmap[entry["matchday"]][team_id] = entry["points_this_matchday"]

        if heatmap:
            sorted_days = sorted(heatmap.keys())
            # Ensure gaps (including matchday 1) are represented with empty scores
            if sorted_days:
                min_md = sorted_days[0]
                if min_md and min_md > 1:
                    for md in range(1, min_md):
                        heatmap.setdefault(md, {})
                for idx in range(len(sorted_days) - 1):
                    current_md = sorted_days[idx]
                    next_md = sorted_days[idx + 1]
                    for md in range(current_md + 1, next_md):
                        heatmap.setdefault(md, {})

        latest_matchday = self.dm.get_latest_matchday(championship_id)
        return {
            "championship_id": championship_id,
            "latest_matchday": latest_matchday,
            "matchdays": [
                {
                    "matchday": md,
                    "scores": heatmap.get(md, {})
                }
                for md in sorted(heatmap.keys())
            ]
        }

    # ------------------------------------------------------------------
    # Player analytics
    # ------------------------------------------------------------------

    def get_player_form(self, championship_id: str, window: int = 5) -> Dict:
        performances = self.dm.get_player_performance_history(championship_id, window=window)
        grouped: Dict[str, List[Dict]] = defaultdict(list)
        for perf in performances:
            grouped[perf["player_id"]].append(perf)

        players: List[Dict] = []
        for player_id, perf_list in grouped.items():
            player_info = self._safe_player_info(player_id)
            if not player_info:
                player_info = {"name": player_id}
            points_series = [p["points"] for p in perf_list]
            avg_points = statistics.mean(points_series) if points_series else 0
            form_trend = 0
            if len(points_series) >= 2:
                diffs = [b - a for a, b in zip(points_series[:-1], points_series[1:])]
                form_trend = statistics.mean(diffs)

            players.append({
                "player_id": player_id,
                "name": player_info.get("name", player_id),
                "matches": len(points_series),
                "average_points": round(avg_points, 2),
                "trend": round(form_trend, 2),
                "last_matchday": perf_list[-1]["matchday"],
                "last_points": perf_list[-1]["points"]
            })

        if not players:
            # Fallback to clause stats when detailed performance history is unavailable
            clause_stats = self.dm.get_clausulable_player_stats(championship_id)
            for entry in clause_stats:
                avg_last_five = entry.get("average_last_five")
                avg_overall = entry.get("average_overall")
                if avg_last_five is None or avg_overall is None:
                    continue
                player_name = entry.get("player_name")
                if not player_name:
                    info = self._safe_player_info(entry.get("player_id"))
                    player_name = info.get("name") if info else entry.get("player_id")

                trend = avg_last_five - avg_overall
                players.append({
                    "player_id": entry.get("player_id"),
                    "name": player_name,
                    "matches": window,
                    "average_points": round(avg_last_five, 2),
                    "trend": round(trend, 2),
                    "last_matchday": None,
                    "last_points": None
                })

        players.sort(key=lambda x: (x["average_points"], x["trend"]), reverse=True)
        return {
            "championship_id": championship_id,
            "window": window,
            "players": players
        }

    def get_player_value_trend(self, championship_id: str, window: int = 30) -> Dict:
        transactions = self.dm.get_transactions_raw(championship_id, days=window)
        price_by_player: Dict[str, List[int]] = defaultdict(list)
        for txn in transactions:
            if txn["price"]:
                price_by_player[txn["player_id"]].append(txn["price"])

        clause_entries = self.dm.get_clausulable_player_stats(championship_id)
        value_trend: List[Dict] = []

        for entry in clause_entries:
            player_id = entry.get("player_id")
            clause_price = entry.get("clause_price") or 0
            suggested = entry.get("suggested_clause") or 0
            avg_last_five = entry.get("average_last_five") or 0
            avg_overall = entry.get("average_overall") or 0
            if not player_id or clause_price is None:
                continue

            player_name = entry.get("player_name")
            if not player_name:
                info = self._safe_player_info(player_id)
                player_name = info.get("name") if info else player_id

            transactions_prices = price_by_player.get(player_id, [])
            avg_txn_price = statistics.mean(transactions_prices) if transactions_prices else None
            last_txn_price = transactions_prices[-1] if transactions_prices else None

            delta_vs_suggested = (suggested - clause_price) if suggested else 0
            efficiency_ratio = (clause_price / avg_last_five) if avg_last_five else None

            value_trend.append({
                "player_id": player_id,
                "name": player_name,
                "market_value": clause_price,
                "suggested_clause": suggested or None,
                "delta_vs_suggested": delta_vs_suggested,
                "average_last_five": round(avg_last_five, 2) if avg_last_five else 0,
                "average_overall": round(avg_overall, 2) if avg_overall else 0,
                "efficiency_ratio": round(efficiency_ratio, 3) if efficiency_ratio else None,
                "last_transaction_price": last_txn_price,
                "average_transaction_price": round(avg_txn_price, 2) if avg_txn_price else None
            })

        value_trend.sort(key=lambda x: (x["delta_vs_suggested"], x.get("market_value", 0)), reverse=True)
        return {
            "championship_id": championship_id,
            "window_days": window,
            "players": value_trend
        }

    # ------------------------------------------------------------------
    # User analytics
    # ------------------------------------------------------------------

    def get_user_consistency(self, championship_id: str, window: Optional[int] = None) -> Dict:
        history = self.dm.get_team_standings_history(championship_id, window)
        teams: Dict[str, Dict] = defaultdict(lambda: {
            "team_id": None,
            "team_name": None,
            "points_series": []
        })

        for entry in history:
            raw_team_id = entry["team_id"]
            team_info = self._resolve_team(championship_id, raw_team_id)
            team_id = team_info.get("team_id") or raw_team_id
            record = teams[team_id]
            record["team_id"] = team_id
            record["team_name"] = team_info.get("team_name", team_id)
            record["points_series"].append(entry["points_this_matchday"])

        results = []
        for record in teams.values():
            series = [p for p in record["points_series"] if p is not None]
            if not series:
                avg = stdev = 0
            else:
                avg = statistics.mean(series)
                stdev = statistics.pstdev(series) if len(series) > 1 else 0

            results.append({
                "team_id": record["team_id"],
                "team_name": record["team_name"],
                "matches": len(series),
                "average_points": round(avg, 2),
                "consistency_index": round(1 / (1 + stdev), 4) if stdev or avg else 0,
                "volatility": round(stdev, 2)
            })

        results.sort(key=lambda x: x["consistency_index"], reverse=True)
        return {
            "championship_id": championship_id,
            "window": window,
            "teams": results
        }

    def get_user_market_activity(self, championship_id: str, window_days: int = 30) -> Dict:
        transactions = self.dm.get_transactions_raw(championship_id, days=window_days)
        clauses = self.dm.get_clauses_raw(championship_id, days=window_days)

        activity: Dict[str, Dict] = {}

        def get_activity_entry(raw_id: Optional[str], fallback_name: Optional[str] = None) -> Optional[Dict]:
            if not raw_id and not fallback_name:
                return None
            info = self._resolve_team(championship_id, raw_id, fallback_name)
            resolved_id = info.get("team_id") or raw_id
            if not resolved_id:
                return None
            if resolved_id not in activity:
                activity[resolved_id] = {
                    "team_id": resolved_id,
                    "team_name": info.get("team_name", resolved_id),
                    "transactions": 0,
                    "spent": 0,
                    "received": 0,
                    "clauses_paid": 0,
                    "clauses_received": 0,
                    "clause_total_paid": 0,
                    "clause_total_received": 0
                }
            else:
                # Ensure latest readable name sticks
                if info.get("team_name"):
                    activity[resolved_id]["team_name"] = info.get("team_name")
            return activity[resolved_id]

        for txn in transactions:
            buyer_team = txn["buyer_team_id"] or txn["buyer_user_id"]
            seller_team = txn["seller_team_id"] or txn["seller_user_id"]

            buyer_entry = get_activity_entry(buyer_team)
            if buyer_entry:
                buyer_entry["transactions"] += 1
                buyer_entry["spent"] += txn["price"] or 0

            seller_entry = get_activity_entry(seller_team)
            if seller_entry:
                seller_entry["transactions"] += 1
                seller_entry["received"] += txn["price"] or 0

        for clause in clauses:
            payer = clause["payer_team_id"] or clause["payer_user_id"]
            receiver = clause["receiver_team_id"] or clause["receiver_user_id"]
            amount = clause["amount"] or 0

            payer_entry = get_activity_entry(payer)
            if payer_entry:
                payer_entry["clauses_paid"] += 1
                payer_entry["clause_total_paid"] += amount

            receiver_entry = get_activity_entry(receiver)
            if receiver_entry:
                receiver_entry["clauses_received"] += 1
                receiver_entry["clause_total_received"] += amount

        results = []
        for record in activity.values():
            # total operations includes both transfers and clauses
            record["operations"] = record["transactions"] + record["clauses_paid"] + record["clauses_received"]
            results.append(record)

        results.sort(key=lambda x: (x["operations"], x["transactions"]), reverse=True)
        return {
            "championship_id": championship_id,
            "window_days": window_days,
            "teams": results
        }

    # ------------------------------------------------------------------
    # Market insights
    # ------------------------------------------------------------------

    def get_market_watchlist(self, championship_id: str, limit: int = 20) -> Dict:
        free_agents = self.dm.get_free_agent_candidates(championship_id)
        watchlist = []

        # Batch get all player info in one query instead of N+1
        player_ids = [fa["player_id"] for fa in free_agents]
        player_info_map = {}
        if player_ids and hasattr(self.dm, 'db'):
            try:
                from app.services.db_connection import get_db
                db = get_db()
                with db.get_connection() as conn:
                    cursor = db.get_cursor(conn)
                    placeholders = ",".join(["%s"] * len(player_ids))
                    cursor.execute(f"SELECT player_id, name, real_team_id, value FROM players WHERE player_id IN ({placeholders})", tuple(player_ids))
                    for row in cursor.fetchall():
                        player_info_map[row[0]] = {"name": row[1], "real_team_id": row[2], "value": row[3] or 0}
            except Exception:
                pass

        for player in free_agents:
            avg_last_five = player.get("average_last_five")
            avg_overall = player.get("average_overall")
            
            # Pick best available average, skip NaN
            average = None
            if avg_last_five is not None and avg_last_five == avg_last_five and avg_last_five > 0:
                average = avg_last_five
            elif avg_overall is not None and avg_overall == avg_overall and avg_overall > 0:
                average = avg_overall
            
            if not average:
                continue

            player_id = player.get("player_id")
            pinfo = player_info_map.get(player_id, {})
            player_name = player.get("name") or pinfo.get("name") or player_id
            team_name = self._resolve_real_team_name(pinfo.get("real_team_id", ""))
            value = pinfo.get("value", 0)
            ratio = round(average / (value / 1_000_000), 3) if value and value > 0 else 0

            watchlist.append({
                "player_id": player_id,
                "name": player_name,
                "team": team_name,
                "average": round(average, 1),
                "clause": value,
                "ratio": ratio,
            })

        # Sort by average descending (best performing free agents first)
        watchlist.sort(key=lambda x: x["average"], reverse=True)
        return {
            "championship_id": championship_id,
            "players": watchlist[:limit]
        }

    def get_clause_network(self, championship_id: str) -> Dict:
        clauses = self.dm.get_clauses_raw(championship_id)
        edges: Dict[str, Dict] = defaultdict(lambda: {
            "source": None,
            "target": None,
            "amount": 0,
            "count": 0
        })

        for clause in clauses:
            payer = clause["payer_team_id"] or clause["payer_user_id"]
            receiver = clause["receiver_team_id"] or clause["receiver_user_id"]
            if not payer or not receiver:
                continue
            key = f"{payer}->{receiver}"
            edge = edges[key]
            edge["source"] = payer
            edge["target"] = receiver
            edge["amount"] += clause["amount"] or 0
            edge["count"] += 1

        network = []
        for edge in edges.values():
            source_team = self._resolve_team(championship_id, edge["source"])
            target_team = self._resolve_team(championship_id, edge["target"])
            network.append({
                "source": edge["source"],
                "source_name": source_team.get("team_name", edge["source"]),
                "target": edge["target"],
                "target_name": target_team.get("team_name", edge["target"]),
                "count": edge["count"],
                "total_amount": edge["amount"]
            })

        network.sort(key=lambda x: x["total_amount"], reverse=True)
        return {
            "championship_id": championship_id,
            "edges": network
        }

    def get_opportunity_streaks(self, championship_id: str, min_streak: int = 3, threshold: float = 6.0) -> Dict:
        latest_matchday = self.dm.get_latest_matchday(championship_id)
        data = self.dm.get_player_streak_data(championship_id)
        streaks = []

        current_player = None
        current_streak = []

        for record in data:
            player_id = record["player_id"]
            points = record["points"] or 0
            if player_id != current_player:
                if current_player and len(current_streak) >= min_streak:
                    streaks.append((current_player, current_streak))
                current_player = player_id
                current_streak = []

            if points >= threshold:
                current_streak.append(record)
            else:
                if current_player and len(current_streak) >= min_streak:
                    streaks.append((current_player, current_streak))
                current_streak = []

        if current_player and len(current_streak) >= min_streak:
            streaks.append((current_player, current_streak))

        formatted = []
        for player_id, streak in streaks:
            player_info = self._safe_player_info(player_id)
            if not player_info:
                player_info = {"name": player_id}
            avg_points = statistics.mean([item["points"] for item in streak]) if streak else 0
            formatted.append({
                "player_id": player_id,
                "name": player_info.get("name", player_id),
                "streak_length": len(streak),
                "average_points": round(avg_points, 2),
                "points": [item["points"] for item in streak],
                "matchdays": [item["matchday"] for item in streak]
            })

        formatted.sort(key=lambda x: (x["streak_length"], x["average_points"]), reverse=True)
        if not formatted:
            clause_stats = self.dm.get_clausulable_player_stats(championship_id)
            for entry in clause_stats:
                avg_last_five = entry.get("average_last_five")
                if avg_last_five is None or avg_last_five < threshold:
                    continue
                player_name = entry.get("player_name")
                if not player_name:
                    info = self._safe_player_info(entry.get("player_id"))
                    player_name = info.get("name") if info else entry.get("player_id")
                formatted.append({
                    "player_id": entry.get("player_id"),
                    "name": player_name,
                    "streak_length": min_streak,
                    "average_points": round(avg_last_five, 2),
                    "points": [],
                    "matchdays": []
                })
            formatted.sort(key=lambda x: (x["average_points"], x["streak_length"]), reverse=True)

        return {
            "championship_id": championship_id,
            "latest_matchday": latest_matchday,
            "streaks": formatted
        }

    # ------------------------------------------------------------------
    # Projections
    # ------------------------------------------------------------------

    def get_matchday_projections(self, championship_id: str, matchday: Optional[int] = None, window: int = 5) -> Dict:
        latest_matchday = self.dm.get_latest_matchday(championship_id)
        target_matchday = matchday or (latest_matchday + 1 if latest_matchday else None)

        odds = self.dm.get_match_odds(championship_id, matchday=target_matchday, upcoming_only=True)
        performances = self.dm.get_player_performance_history(championship_id, window=window)

        form_by_player: Dict[str, List[int]] = defaultdict(list)
        for perf in performances:
            form_by_player[perf["player_id"]].append(perf["points"])

        projections = []
        for match in odds:
            difficulty_home = self._difficulty_from_odds(match.get("odds_home"), match.get("odds_away"))
            difficulty_away = self._difficulty_from_odds(match.get("odds_away"), match.get("odds_home"))
            projections.append({
                "match_id": match["match_id"],
                "matchday": match.get("matchday"),
                "match_date": match.get("match_date"),
                "home": {
                    "team_id": match.get("home_team_id"),
                    "team_name": match.get("home_team_name"),
                    "difficulty": difficulty_home
                },
                "away": {
                    "team_id": match.get("away_team_id"),
                    "team_name": match.get("away_team_name"),
                    "difficulty": difficulty_away
                }
            })

        return {
            "championship_id": championship_id,
            "target_matchday": target_matchday,
            "window": window,
            "matches": projections
        }

    @staticmethod
    def _difficulty_from_odds(team_odds: Optional[float], opponent_odds: Optional[float]) -> Optional[float]:
        if not team_odds:
            return None
        opp = opponent_odds or 1.0
        implied_prob = 1 / team_odds if team_odds else 0
        opp_prob = 1 / opp if opp else 0
        difficulty = opp_prob - implied_prob
        return round(difficulty, 4)


