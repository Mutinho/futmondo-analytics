"""``match_odds`` sync bounded context (pilot domain, lightweight shape).

Extracts ``DataSyncService.sync_match_odds`` into a thin DDD layering while
preserving the exact observable ``SyncResult`` payload (BR1.1, FR5):

- ``domain/ports.py``     — ``MatchOddsSyncDataPort`` (consumer-owned Protocol
                            describing ONLY the data operations this domain
                            consumes; no SQL, no framework — BR2.1).
- ``infrastructure/match_odds_adapter.py`` — ``DataManagerMatchOddsAdapter``,
                            the only place touching ``DataManagerV2`` (wraps the
                            existing calls verbatim — BR2.2).
- ``orchestrator.py``     — ``MatchOddsSyncOrchestrator``, hosting ingestion
                            (injected Futmondo client) + throttling + error
                            handling + delegation, returning the SyncResult dict.

``DataSyncService.sync_match_odds`` becomes a thin delegation to this
orchestrator (same signature, same return).
"""

from app.services.sync.match_odds.orchestrator import MatchOddsSyncOrchestrator

__all__ = ["MatchOddsSyncOrchestrator"]
