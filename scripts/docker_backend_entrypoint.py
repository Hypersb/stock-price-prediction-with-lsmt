"""Start Alembic migrations then the FastAPI research API."""

from __future__ import annotations

import os
import subprocess
import sys


def main() -> int:
    print("running alembic migrations", flush=True)
    subprocess.check_call([sys.executable, "-m", "alembic", "upgrade", "head"])
    host = os.getenv("UVICORN_HOST", "0.0.0.0")
    port = os.getenv("UVICORN_PORT", "8000")
    print(f"starting uvicorn on {host}:{port}", flush=True)
    return subprocess.call(
        [
            sys.executable,
            "-m",
            "uvicorn",
            "backend.app.main:app",
            "--host",
            host,
            "--port",
            port,
        ]
    )


if __name__ == "__main__":
    raise SystemExit(main())
