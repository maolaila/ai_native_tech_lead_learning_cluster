"""核对 HTTP 学习示例的变量和 JSON；实际业务响应仍由 Java/Compose 测试验证。"""
from pathlib import Path
import json
import re
import unittest

ROOT = Path(__file__).resolve().parents[2]
SOURCE = (ROOT / "mini-commerce/api/mini-commerce.http").read_text(encoding="utf-8")


class HttpExampleTest(unittest.TestCase):
    def test_every_placeholder_is_declared(self):
        declared = set(re.findall(r"^@(\w+)\s*=", SOURCE, re.M))
        used = set(re.findall(r"\{\{(\w+)\}\}", SOURCE))
        self.assertTrue(used)
        self.assertEqual(used - declared, set())

    def test_json_bodies_parse_after_replacing_real_values(self):
        bodies = 0
        for section in re.split(r"^### .*$", SOURCE, flags=re.M):
            lines = [line for line in section.splitlines() if not line.startswith("#")]
            block = "\n".join(lines)
            if "Content-Type: application/json" not in block:
                continue
            body = block.split("Content-Type: application/json", 1)[1].strip()
            body = body.replace("{{productId}}", "1")
            self.assertIsInstance(json.loads(body), dict)
            bodies += 1
        self.assertEqual(bodies, 4, "登录、购物车、下单、支付四个 JSON 请求都需校验")

    def test_first_order_uses_actual_request_fields_and_no_coupon(self):
        section = SOURCE.split("### A5.", 1)[1].split("### A6.", 1)[0]
        body = section.split("Content-Type: application/json", 1)[1].strip()
        request = json.loads(body.replace("{{productId}}", "1"))
        self.assertEqual(set(request), {"items"})
        self.assertEqual(set(request["items"][0]), {"productId", "quantity"})
        self.assertIn("Idempotency-Key: {{orderKey}}", section)

    def test_same_request_uses_separate_order_payment_refund_keys(self):
        for name in ("orderKey", "paymentKey", "refundKey"):
            self.assertEqual(SOURCE.count("Idempotency-Key: {{" + name + "}}"), 1)
        self.assertIn("禁止“运行全部”", SOURCE)
        self.assertIn("不会自动清空购物车", SOURCE)


if __name__ == "__main__":
    unittest.main()
