"""Tests dirigidos del helper `record_degraded_step` (FR3.1.1 / BR1).

Congelan el contrato del marcador de degradación de un paso de sync no crítico:
escribe `progress[step]` con `status="degraded"`, `reason` y los `extra`
provistos, y emite un `logger.warning` estructurado con los campos `sync_step` y
`reason`. Es el manejador de un fallo YA capturado: registra, NO re-propaga.

No hay red ni BD: el `ProgressSink` es un doble en memoria (dict).
"""

import logging

import pytest

from app.services.sync_step_status import (
    StepStatus,
    record_degraded_step,
)


class _FakeSink:
    """In-memory ProgressSink double mirroring TaskManager.update_progress."""

    def __init__(self):
        self.progress: dict = {}

    def update_progress(self, task_id: str, step: str, data: dict) -> None:
        self.progress[step] = data


def test_step_status_constants():
    assert StepStatus.RUNNING == "running"
    assert StepStatus.DONE == "done"
    assert StepStatus.DEGRADED == "degraded"


def test_record_degraded_step_writes_degraded_payload_with_extra():
    sink = _FakeSink()

    record_degraded_step(
        sink, "task-1", "prizes", "boom", {"records_synced": 0}
    )

    step_data = sink.progress["prizes"]
    assert step_data["status"] == "degraded"
    assert step_data["reason"] == "boom"
    assert step_data["records_synced"] == 0
    # It records a degradation, never a success.
    assert step_data["status"] != StepStatus.DONE


def test_record_degraded_step_without_extra_has_minimal_payload():
    sink = _FakeSink()

    record_degraded_step(sink, "task-1", "phantoms", "network down")

    step_data = sink.progress["phantoms"]
    assert step_data == {"status": "degraded", "reason": "network down"}


def test_record_degraded_step_does_not_raise():
    sink = _FakeSink()
    # A helper for an ALREADY-caught failure must never re-raise (CT1/BR1).
    record_degraded_step(sink, "task-1", "prizes", "boom")
    assert sink.progress["prizes"]["status"] == "degraded"


def test_record_degraded_step_emits_structured_warning(caplog):
    sink = _FakeSink()

    with caplog.at_level(logging.WARNING, logger="app.services.sync_step_status"):
        record_degraded_step(sink, "task-1", "prizes", "boom", {"records_synced": 0})

    warnings = [r for r in caplog.records if r.levelno == logging.WARNING]
    assert warnings, "expected a structured warning to be emitted"
    record = warnings[-1]
    assert record.sync_step == "prizes"
    assert record.reason == "boom"
