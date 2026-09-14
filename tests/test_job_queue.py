"""Tests for in-process job queue skeleton."""

from __future__ import annotations

import pytest

from backend.app.jobs import InProcessJobQueue


def test_submit_execute_succeeds() -> None:
    queue = InProcessJobQueue()
    queue.register("echo", lambda payload: {"echo": payload.get("value")})
    job = queue.submit("echo", {"value": 7})
    assert job.status == "queued"
    done = queue.execute(job.job_id)
    assert done.status == "succeeded"
    assert done.result == {"echo": 7}
    assert queue.get(job.job_id) is done
    assert len(queue.list()) == 1


def test_execute_failure_records_error() -> None:
    queue = InProcessJobQueue()

    def boom(_payload):
        raise RuntimeError("nope")

    queue.register("boom", boom)
    job = queue.submit("boom", {})
    done = queue.execute(job.job_id)
    assert done.status == "failed"
    assert done.error is not None
    assert "RuntimeError" in done.error


def test_submit_unknown_type_raises() -> None:
    queue = InProcessJobQueue()
    with pytest.raises(KeyError, match="no handler"):
        queue.submit("missing", {})


def test_cancel_queued_job() -> None:
    queue = InProcessJobQueue()
    queue.register("noop", lambda payload: {})
    job = queue.submit("noop", {})
    cancelled = queue.cancel(job.job_id)
    assert cancelled.status == "cancelled"
    # execute is a no-op after cancel
    again = queue.execute(job.job_id)
    assert again.status == "cancelled"
