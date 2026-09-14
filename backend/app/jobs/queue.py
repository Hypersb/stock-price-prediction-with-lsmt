"""In-process job queue skeleton (synchronous execution for now)."""

from __future__ import annotations

import traceback
import uuid
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Literal

JobStatus = Literal["queued", "running", "succeeded", "failed", "cancelled"]


@dataclass
class JobRecord:
    """Mutable job lifecycle record."""

    job_id: str
    job_type: str
    status: JobStatus = "queued"
    payload: dict[str, Any] = field(default_factory=dict)
    result: dict[str, Any] | None = None
    error: str | None = None
    created_at: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    started_at: datetime | None = None
    finished_at: datetime | None = None


class InProcessJobQueue:
    """Simple in-memory queue with a callable registry.

    ``execute`` runs synchronously for the initial skeleton — no worker pool.
    """

    def __init__(self) -> None:
        self._jobs: dict[str, JobRecord] = {}
        self._handlers: dict[str, Callable[[dict[str, Any]], dict[str, Any]]] = {}

    def register(
        self,
        job_type: str,
        handler: Callable[[dict[str, Any]], dict[str, Any]],
    ) -> None:
        if not job_type.strip():
            raise ValueError("job_type must be non-empty")
        self._handlers[job_type] = handler

    def submit(self, job_type: str, payload: dict[str, Any] | None = None) -> JobRecord:
        if job_type not in self._handlers:
            raise KeyError(f"no handler registered for job_type={job_type!r}")
        job = JobRecord(
            job_id=str(uuid.uuid4()),
            job_type=job_type,
            status="queued",
            payload=dict(payload or {}),
        )
        self._jobs[job.job_id] = job
        return job

    def get(self, job_id: str) -> JobRecord | None:
        return self._jobs.get(job_id)

    def list(self) -> list[JobRecord]:
        return sorted(self._jobs.values(), key=lambda j: j.created_at)

    def execute(self, job_id: str) -> JobRecord:
        job = self._jobs.get(job_id)
        if job is None:
            raise KeyError(f"unknown job_id={job_id!r}")
        if job.status == "cancelled":
            return job
        if job.status in {"succeeded", "failed"}:
            return job
        handler = self._handlers.get(job.job_type)
        if handler is None:
            job.status = "failed"
            job.error = f"no handler for {job.job_type}"
            job.finished_at = datetime.now(timezone.utc)
            return job

        job.status = "running"
        job.started_at = datetime.now(timezone.utc)
        try:
            result = handler(dict(job.payload))
            if not isinstance(result, dict):
                raise TypeError("job handler must return a dict")
            job.result = result
            job.status = "succeeded"
            job.error = None
        except Exception as exc:  # noqa: BLE001 — surface failure on job record
            job.status = "failed"
            job.error = f"{type(exc).__name__}: {exc}"
            job.result = {"traceback": traceback.format_exc()}
        job.finished_at = datetime.now(timezone.utc)
        return job

    def cancel(self, job_id: str) -> JobRecord:
        job = self._jobs.get(job_id)
        if job is None:
            raise KeyError(f"unknown job_id={job_id!r}")
        if job.status in {"succeeded", "failed"}:
            return job
        job.status = "cancelled"
        job.finished_at = datetime.now(timezone.utc)
        return job
