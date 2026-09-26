"""The outside watcher (published as the public repo exquest/assay-watch; this copy is its source and is tested
here). Fetches Assay's /health and sends Pushover when the answer is not 200 or the ledger is not ready. Keeps no
state: while Assay is down it alerts on every run. Standard library only."""
from __future__ import annotations

import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request

HEALTH = os.environ.get("ASSAY_HEALTH_URL", "https://assay.cascadiantech.com/health")


def problem(status: int | None, body: bytes, error: str | None = None) -> str | None:
    """None when healthy; otherwise what is wrong, in words."""
    if error is not None:
        return f"health check failed: {error}"
    if status != 200:
        return f"/health answered HTTP {status}: {body[:300].decode(errors='replace')}"
    try:
        h = json.loads(body)
    except ValueError:
        return "/health answered 200 with a body that is not JSON"
    if h.get("ledger") != "ready":
        return f"/health answered 200 but the ledger is {h.get('ledger')!r}"
    return None


def fetch(url: str) -> tuple[int | None, bytes, str | None]:
    req = urllib.request.Request(url, headers={"User-Agent": "assay-watch/1"})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return r.status, r.read(), None
    except urllib.error.HTTPError as e:
        return e.code, e.read(), None
    except Exception as e:
        return None, b"", f"{type(e).__name__}: {e}"


def alert(message: str) -> None:
    data = urllib.parse.urlencode({"token": os.environ["PUSHOVER_APP_TOKEN"], "user": os.environ["PUSHOVER_USER_KEY"],
                                   "title": "Assay watcher: unhealthy", "message": message[:1024],
                                   "priority": "1"}).encode()
    urllib.request.urlopen("https://api.pushover.net/1/messages.json", data=data, timeout=30).read()


def main() -> int:
    p = problem(*fetch(HEALTH))
    if p is None:
        print("healthy")
        return 0
    print(p)
    alert(f"{p} ({HEALTH})")
    return 1


if __name__ == "__main__":
    sys.exit(main())
