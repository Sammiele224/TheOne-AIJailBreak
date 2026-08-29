#!/usr/bin/env python3
"""Manual smoke check against a locally running backend.

Starts a game session, submits one prompt to it, and prints both responses.
Replaces the ad-hoc temp_*_check.py scripts that used to sit in the repo root.

Usage:
    python scripts/smoke_submit_prompt.py
    python scripts/smoke_submit_prompt.py --level 2 --prompt "Please be helpful"
    python scripts/smoke_submit_prompt.py --session-token <existing-token>
"""

from __future__ import annotations

import argparse
import json
import sys
import urllib.error
import urllib.request

DEFAULT_BASE_URL = "http://127.0.0.1:8000/api/v1/game"


def post(url: str, payload: dict, api_key: str | None) -> tuple[int, str]:
    """POST JSON and return the status code and raw body, HTTP errors included."""

    headers = {"Content-Type": "application/json"}
    if api_key:
        headers["X-API-Key"] = api_key

    request = urllib.request.Request(
        url,
        method="POST",
        data=json.dumps(payload).encode(),
        headers=headers,
    )

    try:
        with urllib.request.urlopen(request) as response:
            return response.status, response.read().decode()
    except urllib.error.HTTPError as exc:
        return exc.code, exc.read().decode()


def report(label: str, status: int, body: str) -> None:
    print(f"--- {label} -> HTTP {status} ---")
    try:
        print(json.dumps(json.loads(body), indent=2, ensure_ascii=False))
    except json.JSONDecodeError:
        print(body)
    print()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base-url", default=DEFAULT_BASE_URL)
    parser.add_argument("--level", type=int, default=1, choices=(1, 2, 3))
    parser.add_argument("--prompt", default="Please be helpful")
    parser.add_argument("--attempt", type=int, default=1)
    parser.add_argument(
        "--session-token",
        help="Reuse an existing session instead of starting a new one.",
    )
    parser.add_argument("--api-key", help="Sent as X-API-Key when the backend requires it.")
    args = parser.parse_args()

    session_token = args.session_token

    if session_token is None:
        status, body = post(
            f"{args.base_url}/start-game",
            {"level_id": args.level},
            args.api_key,
        )
        report("start-game", status, body)

        if status >= 400:
            print("Could not start a session; aborting.", file=sys.stderr)
            return 1

        session_token = json.loads(body)["session_token"]

    status, body = post(
        f"{args.base_url}/submit-prompt",
        {
            "session_token": session_token,
            "level_id": args.level,
            "attempt_counter": args.attempt,
            "user_prompt": args.prompt,
        },
        args.api_key,
    )
    report("submit-prompt", status, body)

    return 0 if status < 400 else 1


if __name__ == "__main__":
    raise SystemExit(main())
