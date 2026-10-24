"""Characterization + extraction tests for ``PlayersFullSyncOrchestrator`` (BR1.1,
BR1.2, BR5.1, BR5.3).

Methodology: test-after, characterization-first (see the approved Testing
Contract). The ``_Characterization`` group freezes the CURRENT observable
behavior — which fields the orchestrator assembles into ``player_records`` /
``stats_payload``, the favorites selection rule (``fav`` True AND no
``userteamId``), the error-path with no credential leak, and the preserved
``SyncResult`` payload. The ``_Extraction`` group asserts the NEW behavior: the
six enriched fields reach ``player_records`` with ``clean_float``
normalization of ``homeAverage``/``awayAverage`` (incl. the verified ``"NaN"``
string case) while the rest of the payload stays byte-identical.

No real DB, no network, no credentials: a deterministic client double returns
the verified raw ``/5/league/championshipplayers`` player shape, and a
recording port fake captures the assembled payloads. ``time.sleep`` is a no-op.
"""

import os

os.environ.setdefault("JWT_SECRET", "test-secret-not-default-000")

import app.services.sync.players_full.orchestrator as orch_mod  # noqa: E402
from app.services.sync.players_full import PlayersFullSyncOrchestrator  # noqa: E402

CHAMPIONSHIP_ID = "592416daa3a2dd871a7a9956"


class _RecordingPort:
    """Minimal recording double for ``PlayersFullSyncDataPort``."""

    def __init__(self, batch_count=0, orphans=0):
        self._batch_count = batch_count
        self._orphans = orphans
        self.players_batches = []
        self.orphan_calls = []
        self.stats_calls = []
        self.favorites_calls = []
        self.metadata = []

    def save_players_batch(self, player_records):
        self.players_batches.append([dict(r) for r in player_records])
        return self._batch_count

    def delete_orphan_players(self, live_ids):
        self.orphan_calls.append(list(live_ids))
        return self._orphans

    def save_player_championship_stats(self, championship_id, stats_payload):
        self.stats_calls.append(
            {"championship_id": championship_id, "stats": [dict(s) for s in stats_payload]}
        )

    def save_favorites(self, championship_id, user_id, player_ids):
        self.favorites_calls.append(
            {"championship_id": championship_id, "user_id": user_id, "player_ids": list(player_ids)}
        )

    def update_sync_metadata(self, **kwargs):
        self.metadata.append(kwargs)


class _FakeFutmondoClient:
    """Return the verified raw player shape; raise on demand. No network."""

    def __init__(self, players_data=None, raises=None, user_id="user-42"):
        self._players_data = players_data
        self._raises = raises
        self.user_id = user_id
        # A credential-like attribute that must NEVER appear in any log/error.
        self.password = "super-secret-password"
        self.token = "super-secret-token"

    def get_championship_players(self, championship_id):
        if self._raises is not None:
            raise self._raises
        return self._players_data


def _verified_player(**over):
    """A player as ``/5/league/championshipplayers`` returns it (verified
    2026-10-24): ``points``/``change``/``status`` top-level, ``average`` a dict
    with ``homeAverage``/``awayAverage`` as STRINGS (possibly ``"NaN"``) and
    ``matches``."""
    base = {
        "id": "p1",
        "name": "Striker",
        "role": "delantero",
        "role2": "",
        "teamId": "504e581e4d8bec9a670000c6",
        "team": "Real Madrid",
        "slug": "striker",
        "photo": "striker.png",
        "value": 5000000,
        "points": 123,
        "change": -40000,
        "status": "ok",
        "average": {
            "average": "6.5",
            "averageLastFive": "7.0",
            "homeAverage": "6.2",
            "awayAverage": "5.8",
            "matches": 12,
        },
        "clause": {"price": 9000000, "suggestedClause": 9500000, "date": "2026-10-24"},
    }
    base.update(over)
    return base


def _run(monkeypatch, players, user_id="user-42", batch_count=None, raises=None):
    monkeypatch.setattr(orch_mod.time, "sleep", lambda *a, **k: None)
    client = _FakeFutmondoClient(
        players_data={"players": players} if players is not None else {"players": []},
        raises=raises,
        user_id=user_id,
    )
    port = _RecordingPort(batch_count=batch_count if batch_count is not None else len(players or []))
    orchestrator = PlayersFullSyncOrchestrator(
        client=client, championship_id=CHAMPIONSHIP_ID, data=port
    )
    result = orchestrator.sync()
    return result, port


# ======================================================================
# Characterization — freeze CURRENT observable behavior.
# ======================================================================
class TestCharacterization:
    def test_player_records_assembled_fields_present(self, monkeypatch):
        """The record carries at least the historical identity/value fields."""
        _, port = _run(monkeypatch, [_verified_player()])
        rec = port.players_batches[0][0]
        for key in ("id", "name", "role", "role2", "teamId", "team", "slug", "photo", "value"):
            assert key in rec
        assert rec["id"] == "p1"
        assert rec["value"] == 5000000

    def test_stats_payload_shape_unchanged(self, monkeypatch):
        """stats_payload maps clause/average fields exactly as before."""
        _, port = _run(monkeypatch, [_verified_player()])
        stats = port.stats_calls[0]["stats"][0]
        assert stats["player_id"] == "p1"
        assert stats["clause_price"] == 9000000
        assert stats["suggested_clause"] == 9500000
        assert stats["average_last_five"] == "7.0"
        assert stats["average_overall"] == "6.5"

    def test_favorites_selection_fav_true_and_no_userteam(self, monkeypatch):
        """Only fav==True AND no userteamId is a favorite; user_id from client."""
        players = [
            _verified_player(id="fav", fav=True),
            _verified_player(id="owned", fav=True, userteamId="ut9"),
            _verified_player(id="plain"),
        ]
        _, port = _run(monkeypatch, players)
        assert port.favorites_calls[0]["player_ids"] == ["fav"]
        assert port.favorites_calls[0]["user_id"] == "user-42"

    def test_syncresult_payload_preserved_on_success(self, monkeypatch):
        result, _ = _run(monkeypatch, [_verified_player()], batch_count=1)
        assert set(result.keys()) == {"status", "records_synced", "duration_seconds"}
        assert result["status"] == "success"
        assert result["records_synced"] == 1
        assert isinstance(result["duration_seconds"], float)

    def test_error_path_preserves_payload_and_leaks_no_credentials(self, monkeypatch):
        """Fatal ingestion error → status error; no password/token in payload."""
        result, port = _run(
            monkeypatch, None, raises=RuntimeError("timeout on /championshipPlayers")
        )
        assert result["status"] == "error"
        assert set(result.keys()) == {"status", "error", "duration_seconds"}
        assert "super-secret-password" not in result["error"]
        assert "super-secret-token" not in result["error"]
        assert "password" not in result["error"].lower()
        assert "token" not in result["error"].lower()
        assert port.players_batches == []
        assert port.metadata[0]["sync_status"] == "error"


# ======================================================================
# Extraction — the NEW six enriched fields reach player_records.
# ======================================================================
class TestExtraction:
    def test_six_enriched_fields_extracted(self, monkeypatch):
        _, port = _run(monkeypatch, [_verified_player()])
        rec = port.players_batches[0][0]
        assert rec["points"] == 123
        assert rec["change"] == -40000
        assert rec["matches"] == 12
        assert rec["status"] == "ok"
        assert rec["home_average"] == 6.2
        assert rec["away_average"] == 5.8

    def test_nan_string_averages_normalized_to_none(self, monkeypatch):
        player = _verified_player(
            average={"average": "6.5", "homeAverage": "NaN", "awayAverage": "NaN", "matches": 3}
        )
        _, port = _run(monkeypatch, [player])
        rec = port.players_batches[0][0]
        assert rec["home_average"] is None
        assert rec["away_average"] is None
        assert rec["matches"] == 3

    def test_empty_and_missing_averages_default(self, monkeypatch):
        player = _verified_player(average={"average": "6.5"})  # no home/away/matches
        player.pop("points")
        player.pop("change")
        player.pop("status")
        _, port = _run(monkeypatch, [player])
        rec = port.players_batches[0][0]
        assert rec["home_average"] is None
        assert rec["away_average"] is None
        assert rec["matches"] == 0
        assert rec["points"] == 0
        assert rec["change"] == 0
        assert rec["status"] == ""

    def test_null_average_dict_does_not_break(self, monkeypatch):
        player = _verified_player(average=None)
        _, port = _run(monkeypatch, [player])
        rec = port.players_batches[0][0]
        assert rec["home_average"] is None
        assert rec["away_average"] is None
        assert rec["matches"] == 0

    def test_syncresult_unchanged_with_enrichment(self, monkeypatch):
        """Enrichment must not alter the returned SyncResult contract."""
        result, _ = _run(monkeypatch, [_verified_player()], batch_count=1)
        assert set(result.keys()) == {"status", "records_synced", "duration_seconds"}
        assert result["status"] == "success"
        assert result["records_synced"] == 1

    def test_stats_payload_byte_identical_with_enrichment(self, monkeypatch):
        """The enriched extraction must not touch stats_payload mapping."""
        _, port = _run(monkeypatch, [_verified_player()])
        stats = port.stats_calls[0]["stats"][0]
        assert stats == {
            "player_id": "p1",
            "owner_team_id": None,
            "owner_team_name": None,
            "owner_user_id": None,
            "clause_price": 9000000,
            "suggested_clause": 9500000,
            "clause_date": "2026-10-24",
            "average_last_five": "7.0",
            "average_overall": "6.5",
        }
