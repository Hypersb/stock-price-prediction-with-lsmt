"""Print non-secret effective backend configuration."""

from __future__ import annotations

import json
import sys

from backend.app.core.config import (
    assert_summary_has_no_secrets,
    get_settings,
)


def main() -> int:
    settings = get_settings()
    summary = settings.safe_settings_summary()
    assert_summary_has_no_secrets(summary)
    json.dump(summary, sys.stdout, indent=2, sort_keys=True)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
