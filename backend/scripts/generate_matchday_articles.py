#!/usr/bin/env python3
"""
Utility script to backfill humorous matchday articles.

Usage examples:
    python backend/scripts/generate_matchday_articles.py --start 1 --end 12
    python backend/scripts/generate_matchday_articles.py --force
"""

import argparse
import logging
import sys
from pathlib import Path
from typing import Optional

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from app.core.config import CHAMPIONSHIP_ID  # noqa: E402
from app.services.data_manager_v2 import DataManagerV2  # noqa: E402
from app.services.matchday_humor_service import MatchdayHumorService  # noqa: E402


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate and persist humorous matchday articles."
    )
    parser.add_argument(
        "--championship-id",
        default=CHAMPIONSHIP_ID,
        help="Championship ID to use (defaults to configured CHAMPIONSHIP_ID).",
    )
    parser.add_argument(
        "--start",
        type=int,
        default=1,
        help="First matchday to generate (inclusive).",
    )
    parser.add_argument(
        "--end",
        type=int,
        default=None,
        help="Last matchday to generate (inclusive). Defaults to latest matchday in DB.",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Force regeneration even if an article already exists.",
    )
    return parser.parse_args()


def generate_articles(
    championship_id: str,
    start_matchday: int,
    end_matchday: Optional[int],
    force: bool,
):
    logging.info("Initializing data manager and humor service...")
    data_manager = DataManagerV2(skip_init=True)
    humor_service = MatchdayHumorService(data_manager=data_manager)

    latest_in_db = data_manager.get_latest_matchday(championship_id) or 0
    if latest_in_db == 0:
        logging.warning(
            "No team standings found for championship %s. Aborting.", championship_id
        )
        return

    final_matchday = end_matchday or latest_in_db
    if final_matchday > latest_in_db:
        logging.info(
            "Requested end matchday %s exceeds latest (%s). Truncating.",
            final_matchday,
            latest_in_db,
        )
        final_matchday = latest_in_db

    generated = 0
    skipped = 0
    for matchday in range(start_matchday, final_matchday + 1):
        try:
            logging.info("Processing matchday %s...", matchday)
            humor_service.get_or_generate_article(
                championship_id=championship_id,
                matchday=matchday,
                force_refresh=force,
            )
            generated += 1
        except Exception as exc:  # pylint: disable=broad-except
            logging.error(
                "Failed to generate article for matchday %s: %s", matchday, exc
            )
            skipped += 1

    logging.info(
        "Done. Generated %s articles, skipped/failures %s (range %s-%s).",
        generated,
        skipped,
        start_matchday,
        final_matchday,
    )


def main():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
    )

    args = parse_args()
    generate_articles(
        championship_id=args.championship_id,
        start_matchday=args.start,
        end_matchday=args.end,
        force=args.force,
    )


if __name__ == "__main__":
    main()

