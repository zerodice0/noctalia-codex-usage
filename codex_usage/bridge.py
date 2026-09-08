#!/usr/bin/env python3
"""Read Codex quota metadata over the documented app-server stdio protocol.

No model turns, direct credential reads, third-party endpoints or dependencies.
Only allowlisted quota fields leave this process; raw server errors are private.
"""

import argparse
import json
import math
import os
from pathlib import Path
import selectors
import shutil
import subprocess
import time


class BridgeError(Exception):
    def __init__(self, code):
        self.code = code
        super().__init__(code)


def executable(configured=""):
    if configured:
        found = shutil.which(os.path.expanduser(configured))
        if found:
            return found
        raise BridgeError("codex_missing")
    found = shutil.which("codex")
    if found:
        return found
    # GUI sessions do not always inherit the interactive terminal's PATH.
    for candidate in (
        Path.home() / ".local/bin/codex",
        Path("/home/linuxbrew/.linuxbrew/bin/codex"),
        Path("/usr/local/bin/codex"),
        Path("/usr/bin/codex"),
    ):
        if candidate.is_file() and os.access(candidate, os.X_OK):
            return str(candidate)
    raise BridgeError("codex_missing")


def classify_error(error):
    message = str(error.get("message", "")).lower() if isinstance(error, dict) else ""
    if any(word in message for word in ("not logged", "unauthorized", "401", "sign in", "authentication", "refresh token")):
        return "login_required"
    if any(word in message for word in ("api key", "api-key", "chatgpt account")):
        return "chatgpt_required"
    if "method not found" in message:
        return "upgrade_codex"
    return "request_failed"


class RpcClient:
    def __init__(self, command, timeout=20):
        self.deadline = time.monotonic() + timeout
        self.buffer = b""
        self.proc = subprocess.Popen(
            command, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL, cwd=Path.home(),
        )
        self.selector = selectors.DefaultSelector()
        self.selector.register(self.proc.stdout, selectors.EVENT_READ)

    def send(self, message):
        self.proc.stdin.write((json.dumps(message) + "\n").encode())
        self.proc.stdin.flush()

    def request(self, request_id, method, params=None):
        message = {"id": request_id, "method": method}
        if params is not None:
            message["params"] = params
        self.send(message)
        while True:
            remaining = self.deadline - time.monotonic()
            if remaining <= 0:
                raise BridgeError("timeout")
            if b"\n" in self.buffer:
                line, self.buffer = self.buffer.split(b"\n", 1)
                try:
                    reply = json.loads(line)
                except (ValueError, UnicodeDecodeError):
                    raise BridgeError("invalid_response") from None
                if not isinstance(reply, dict):
                    raise BridgeError("invalid_response")
                if reply.get("id") != request_id:
                    # Ignore notifications; reject unexpected server requests.
                    if "id" in reply and "method" in reply:
                        self.send({"id": reply["id"], "error": {"code": -32601, "message": "Unsupported by quota reader"}})
                    continue
                if "error" in reply:
                    raise BridgeError(classify_error(reply["error"]))
                if not isinstance(reply.get("result"), dict):
                    raise BridgeError("invalid_response")
                return reply["result"]
            if not self.selector.select(remaining):
                raise BridgeError("timeout")
            chunk = os.read(self.proc.stdout.fileno(), 65536)
            if not chunk:
                raise BridgeError("server_closed")
            self.buffer += chunk
            if len(self.buffer) > 4 * 1024 * 1024:
                raise BridgeError("invalid_response")

    def close(self):
        self.selector.close()
        if self.proc.poll() is None:
            self.proc.terminate()
            try:
                self.proc.wait(timeout=2)
            except subprocess.TimeoutExpired:
                self.proc.kill()
                self.proc.wait()
        self.proc.stdin.close()
        self.proc.stdout.close()


def number(value):
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value)


def normalize(result, fetched_at=None):
    buckets = result.get("rateLimitsByLimitId")
    if not isinstance(buckets, dict) or not buckets:
        legacy = result.get("rateLimits")
        buckets = {legacy.get("limitId") or "codex": legacy} if isinstance(legacy, dict) else {}
    normalized = []
    for key, bucket in sorted(buckets.items(), key=lambda entry: (entry[0] != "codex", entry[0])):
        if not isinstance(bucket, dict):
            continue
        windows = []
        for kind in ("primary", "secondary"):
            window = bucket.get(kind)
            if not isinstance(window, dict) or not number(window.get("usedPercent")):
                continue
            minutes, reset = window.get("windowDurationMins"), window.get("resetsAt")
            windows.append({
                "kind": kind,
                "usedPercent": max(0, min(100, window["usedPercent"])),
                "windowDurationMins": minutes if number(minutes) and minutes > 0 else None,
                "resetsAt": int(reset) if number(reset) and 0 < reset < 253402300800 else None,
            })
        windows.sort(key=lambda window: window["windowDurationMins"] or float("inf"))
        if windows:
            normalized.append({
                "id": str(key)[:120],
                "name": str(bucket.get("limitName") or key)[:120],
                "plan": str(bucket.get("planType") or "")[:40],
                "windows": windows,
            })
    return {
        "ok": bool(normalized),
        "error": None if normalized else "no_limits",
        "fetchedAt": int(time.time() if fetched_at is None else fetched_at),
        "buckets": normalized,
    }


def fetch(codex="", timeout=20):
    client = RpcClient([executable(codex), "app-server", "--stdio", "-c", "analytics.enabled=false"], timeout)
    try:
        client.request(0, "initialize", {"clientInfo": {
            "name": "noctalia_codex_usage", "title": "Noctalia Codex Usage", "version": "0.1.0",
        }})
        client.send({"method": "initialized", "params": {}})
        return normalize(client.request(1, "account/rateLimits/read"))
    finally:
        client.close()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--codex", default="", help="Codex executable path (auto-detected by default)")
    parser.add_argument("--timeout", type=float, default=20)
    args = parser.parse_args()
    try:
        result = fetch(args.codex, max(1, min(25, args.timeout)))
    except BridgeError as error:
        result = {"ok": False, "error": error.code, "buckets": []}
    except (OSError, ValueError):
        result = {"ok": False, "error": "server_failed", "buckets": []}
    print(json.dumps(result, ensure_ascii=False, allow_nan=False))


if __name__ == "__main__":
    main()
