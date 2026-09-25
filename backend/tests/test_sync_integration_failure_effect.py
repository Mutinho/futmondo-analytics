"""Effect specs — sync integration-failure classification (u2-integrations).

Q1 floor: assert the EFFECT, never a bare ``pytest.raises``.

Recoverable failure (timeout/unparseable/request) at a non-critical step ->
the step is marked ``DEGRADED`` via ``SyncStepStatus`` AND the sync does NOT fail
(BR3.1). Fatal failure (ban) -> the exception propagates so the task is marked
FAILED AND no half-written data survives (BR3.2/NFR2).

These exercise the real capture point in ``sync._run_sync_in_background`` with a
fake ``ProgressSink`` (records ``progress[step]``) and a monkeypatched
``DataSyncService`` whose ``sync_prizes`` raises the typed integration error. No
network, no real DB, no real credentials.
"""

import pytest

import app.api.v1.endpoints.sync as sync_mod
from app.services.integration_errors import (
    IntegrationBanError,
    IntegrationRequestError,
    IntegrationTimeoutError,
)
from app.services.sync_step_status import StepStatus


class _FakeTaskService:
    """In-memory ProgressSink + task lifecycle recorder (no DB, no network)."""

    def __init__(self):
        self.progress = {}
        self.status = None
        self.failed_reason = None
        self.completed_results = None

    # ProgressSink contract
    def update_progress(self, task_id, step, data):
        self.progress[step] = data

    def mark_running(self, task_id, step=None):
        self.status = "running"

    def mark_failed(self, task_id, reason):
        self.status = "failed"
        self.failed_reason = reason

    def mark_completed(self, task_id, results):
        self.status = "completed"
        self.completed_results = results


class _FakeSyncService:
    """Stands in for DataSyncService: every step is a no-op except sync_prizes."""

    def __init__(self, prizes_exc=None):
        self._prizes_exc = prizes_exc
        self.championship_id = "c1"

        class _DM:
            def update_sync_metadata(self, **kwargs):
                return None

        self.dm = _DM()

    def _ok(self, *a, **k):
        return {"records_synced": 0}

    # All the "all" steps before prizes are no-op successes.
    sync_players_full = _ok
    sync_transactions = _ok
    sync_clauses = _ok
    sync_punishments_bonuses = _ok
    sync_dream_teams_mvps = _ok
    sync_player_performance = _ok
    sync_rosters = _ok
    sync_round_rankings = _ok
    sync_match_odds = _ok

    def sync_prizes(self):
        if self._prizes_exc is not None:
            raise self._prizes_exc
        return {"records_synced": 3, "status": "success"}


def _run_with(monkeypatch, prizes_exc):
    fake_tm = _FakeTaskService()
    monkeypatch.setattr(sync_mod, "get_task_service", lambda: fake_tm)

    def _fake_ctor(futmondo_client=None):
        return _FakeSyncService(prizes_exc=prizes_exc)

    monkeypatch.setattr(sync_mod, "DataSyncService", _fake_ctor)
    # _check_phantoms consumes the client; stub it to a benign success.
    monkeypatch.setattr(
        sync_mod, "_check_phantoms", lambda cid, client, uid: {"total_phantoms": 0}
    )
    sync_mod._run_sync_in_background(
        task_id="task-1", sync_type="all", championship_id="c1", client=object(), user_id="u1"
    )
    return fake_tm


@pytest.mark.parametrize(
    "rec_exc",
    [
        IntegrationTimeoutError(endpoint="/x"),
        IntegrationRequestError(endpoint="/x"),
    ],
)
def test_recoverable_failure_marks_step_degraded_and_sync_does_not_fail(monkeypatch, rec_exc):
    """EFFECT (BR3.1): recoverable -> prizes step DEGRADED, task still completes."""
    fake_tm = _run_with(monkeypatch, prizes_exc=rec_exc)

    # The step is recorded DEGRADED (not "done", not "failed").
    assert fake_tm.progress["prizes"]["status"] == StepStatus.DEGRADED
    assert "reason" in fake_tm.progress["prizes"]
    # The sync as a whole did NOT fail: it completed.
    assert fake_tm.status == "completed"
    assert fake_tm.failed_reason is None


def test_fatal_ban_propagates_and_marks_task_failed(monkeypatch):
    """EFFECT (BR3.2): fatal ban -> task FAILED (propagated); prizes not 'done'."""
    fake_tm = _run_with(monkeypatch, prizes_exc=IntegrationBanError(status=403, endpoint="/ratings"))

    # The ban propagated out of the prizes handler into the task-level handler.
    assert fake_tm.status == "failed"
    assert fake_tm.failed_reason is not None
    # The prizes step was never marked "done" (no false success / no half data).
    assert fake_tm.progress.get("prizes", {}).get("status") != StepStatus.DONE


def test_success_path_marks_prizes_done(monkeypatch):
    """Sanity: with no failure, prizes completes normally (regression guard).

    Note the existing route merges ``{"status": "done", **prizes_result}``; when
    ``sync_prizes`` returns its own ``status`` key it wins (here ``"success"``).
    The effect asserted is that the step is NOT degraded and the sync completed.
    """
    fake_tm = _run_with(monkeypatch, prizes_exc=None)
    assert fake_tm.progress["prizes"]["status"] != StepStatus.DEGRADED
    assert fake_tm.progress["prizes"]["records_synced"] == 3
    assert fake_tm.status == "completed"
