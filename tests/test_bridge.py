import json
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "codex_usage"))
from bridge import BridgeError, RpcClient, classify_error, normalize


class QuotaTests(unittest.TestCase):
    def test_weekly_primary_is_not_assumed_to_be_five_hours(self):
        result = normalize({"rateLimits": {"primary": {"usedPercent": 25, "windowDurationMins": 10080, "resetsAt": 1789435428}}}, 10)
        self.assertEqual(result["buckets"][0]["windows"], [{"kind": "primary", "usedPercent": 25, "windowDurationMins": 10080, "resetsAt": 1789435428}])

    def test_multi_bucket_view_is_authoritative_and_codex_is_first(self):
        bucket = {"primary": {"usedPercent": 0}}
        result = normalize({"rateLimitsByLimitId": {"spark": bucket, "codex": bucket}, "rateLimits": bucket})
        self.assertEqual([item["id"] for item in result["buckets"]], ["codex", "spark"])

    def test_missing_limits_do_not_look_like_zero_usage(self):
        self.assertEqual(normalize({"rateLimits": None})["error"], "no_limits")
        self.assertEqual(normalize({"rateLimits": {"primary": {"resetsAt": 20}}})["error"], "no_limits")

    def test_unknown_reset_is_preserved_and_percent_is_bounded(self):
        window = normalize({"rateLimits": {"primary": {"usedPercent": 120}}})["buckets"][0]["windows"][0]
        self.assertEqual(window["usedPercent"], 100)
        self.assertIsNone(window["resetsAt"])

    def test_private_fields_are_not_forwarded(self):
        encoded = json.dumps(normalize({"email": "PRIVATE", "rateLimits": {"credits": "PRIVATE", "primary": {"usedPercent": 25, "private": "PRIVATE"}}}))
        self.assertNotIn("PRIVATE", encoded)
        self.assertEqual(classify_error({"message": "401 private sensitive details"}), "login_required")

    def test_buffered_notifications_do_not_hide_response(self):
        program = 'import sys,json; req=json.loads(input()); print(json.dumps({"method":"notice"})+"\\n"+json.dumps({"id":req["id"],"result":{"ok":True}}),flush=True)'
        client = RpcClient([sys.executable, "-u", "-c", program], 2)
        try:
            self.assertEqual(client.request(3, "test"), {"ok": True})
        finally:
            client.close()
        self.assertIsNotNone(client.proc.poll())

    def test_timeout_stops_child(self):
        client = RpcClient([sys.executable, "-u", "-c", 'import time; input(); time.sleep(10)'], 0.1)
        try:
            with self.assertRaises(BridgeError) as error:
                client.request(0, "test")
            self.assertEqual(error.exception.code, "timeout")
        finally:
            client.close()
        self.assertIsNotNone(client.proc.poll())

    def test_nonfinite_percentage_is_not_a_valid_measurement(self):
        for bad in (float("nan"), float("inf"), True, "25"):
            self.assertFalse(normalize({"rateLimits": {"primary": {"usedPercent": bad}}})["ok"])


if __name__ == "__main__":
    unittest.main()
