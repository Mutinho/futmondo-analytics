#!/usr/bin/env python3
"""Initialise database schema without fetching data."""

import logging
import sys

sys.path.insert(0, ".")  # allow running via python scripts/init_db.py

from app.services.data_manager_v2 import DataManagerV2


def main():
    logging.basicConfig(level=logging.INFO)
    logging.info("Resetting database schema (dropping & recreating tables)...")
    DataManagerV2(skip_init=False)
    logging.info("Schema initialised.")


if __name__ == "__main__":
    main()

