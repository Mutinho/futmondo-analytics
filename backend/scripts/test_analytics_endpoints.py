#!/usr/bin/env python3
"""Quick smoke test for analytics endpoints."""

import argparse
import sys
from typing import Dict

import requests


ENDPOINTS = [
    ("championship trends", "/api/v1/analytics/championship/trends", {"window": 5}),
    ("championship custom classification", "/api/v1/analytics/championship/custom-classification", {"window": 5}),
    ("championship heatmap", "/api/v1/analytics/championship/heatmap", {}),
    ("player form", "/api/v1/analytics/players/form", {"window": 5}),
    ("player value trend", "/api/v1/analytics/players/value-trend", {"window_days": 30}),
    ("user consistency", "/api/v1/analytics/users/consistency", {"window": 10}),
    ("user market activity", "/api/v1/analytics/users/market-activity", {"window_days": 30}),
    ("market watchlist", "/api/v1/analytics/market/watchlist", {"limit": 20}),
    ("clause network", "/api/v1/analytics/clauses/network", {}),
    ("opportunities streaks", "/api/v1/analytics/opportunities/streaks", {"min_streak": 3, "threshold": 6}),
    ("matchday projections", "/api/v1/analytics/projections/matchday", {})
]


def request(base_url: str, path: str, params: Dict) -> requests.Response:
    url = base_url.rstrip("/") + path
    try:
        response = requests.get(url, params=params, timeout=30)
        return response
    except Exception as exc:  # pragma: no cover - diagnostic helper
        raise RuntimeError(f"Request to {url} failed: {exc}") from exc


def main() -> int:
    parser = argparse.ArgumentParser(description="Smoke test analytics endpoints")
    parser.add_argument("base_url", help="Base URL of the running backend, e.g. http://localhost:8081")
    parser.add_argument("--championship", help="Override championship_id query param", default=None)
    args = parser.parse_args()

    success = True

    for name, path, params in ENDPOINTS:
        params = dict(params)  # copy
        if args.championship:
            params.setdefault("championship_id", args.championship)

        try:
            response = request(args.base_url, path, params)
        except RuntimeError as exc:
            print(f"[ERROR] {name}: {exc}")
            success = False
            continue

        status = response.status_code
        if status == 200:
            try:
                payload = response.json()
            except ValueError:
                payload = None
            summary = "ok"
            if isinstance(payload, dict):
                summary = f"keys={list(payload.keys())[:3]}"  # quick glance
            print(f"[OK]    {name} → {status} {summary}")
        else:
            success = False
            snippet = response.text[:200].replace("\n", " ")
            print(f"[FAIL]  {name} → {status} {snippet}")

    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())





