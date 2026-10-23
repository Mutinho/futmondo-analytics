"""Narrow read-from-sync layer for latency-sensitive endpoints.

This package serves ``favorites/my`` and the ``market/today`` catalog from the
already-synced Neon tables, replacing the heavy live catalog download. All new
SQL lives here (never in the routers or the god-files), using the parameterized
``db.adapt_params`` pattern. Routers delegate to these functions and fall back
to the existing live route on a sync-miss (0 synced rows). See BR1.1.
"""
