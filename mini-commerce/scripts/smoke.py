#!/usr/bin/env python3
"""只用于本地教学环境的真实 HTTP Smoke，会创建专用演示数据，不删除既有数据。"""
from __future__ import annotations
import json
import os
import sys
import time
import uuid
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse
from urllib.request import Request, urlopen

BASE = os.getenv("BASE_URL", "http://127.0.0.1:18080").rstrip("/")


def request(method: str, path: str, body=None, token=None, key=None):
    headers = {"Accept": "application/json"}
    if token: headers["Authorization"] = "Bearer " + token
    if key: headers["Idempotency-Key"] = key
    data = None
    if body is not None:
        data = json.dumps(body).encode("utf-8")
        headers["Content-Type"] = "application/json"
    try:
        with urlopen(Request(BASE + path, data=data, headers=headers, method=method), timeout=10) as response:
            raw = response.read(1_000_000)
            return json.loads(raw) if raw else None
    except HTTPError as error:
        detail = error.read(2000).decode("utf-8", errors="replace")
        raise RuntimeError(f"{method} {path}: HTTP {error.code}, {detail}") from None


def require(condition: bool, message: str) -> None:
    if not condition: raise RuntimeError(message)


def wait_until(action, predicate, timeout: int, label: str):
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        try:
            value = action()
            if predicate(value): return value
        except (URLError, TimeoutError, RuntimeError, ValueError):
            pass
        time.sleep(1)
    raise RuntimeError(label + " 在限定时间内未满足；检查 docker compose logs --tail=100 backend")


def main() -> None:
    require(urlparse(BASE).hostname in {"localhost", "127.0.0.1", "::1"}, "Smoke 仅接受本机地址，禁止用于生产")
    wait_until(lambda: request("GET", "/actuator/health/readiness"), lambda data: data.get("status") == "UP", 180, "后端健康检查")
    run = uuid.uuid4().hex
    email, password = f"smoke-{run}@example.com", "SmokePassword123!"
    request("POST", "/api/auth/register", {"email": email, "displayName": "Smoke learner", "password": password})
    buyer = request("POST", "/api/auth/login", {"email": email, "password": password})["accessToken"]
    admin = request("POST", "/api/auth/login", {
        "email": os.getenv("SMOKE_ADMIN_EMAIL", "admin@example.com"),
        "password": os.getenv("SMOKE_ADMIN_PASSWORD", "AdminPassword123!"),
    })["accessToken"]
    # 专用商品避免耗尽示例库存，也避免假设数据库主键固定为 1。
    product = request("POST", "/api/products", {"sku": "SMOKE-" + run, "name": "Smoke 商品",
        "description": "本地验收专用", "price": 200, "currency": "CNY", "initialStock": 2}, admin)
    request("POST", f"/api/products/{product['id']}/publication", token=admin)
    require(request("GET", f"/api/products/{product['id']}")["status"] == "PUBLISHED", "商品没有上架")
    body = {"items": [{"productId": product["id"], "quantity": 1}]}
    order = request("POST", "/api/orders", body, buyer, run)
    replay = request("POST", "/api/orders", body, buyer, run)
    require(order["id"] == replay["id"], "同幂等键产生了不同订单")
    require(order["totalAmount"] == 200 and order["currency"] == "CNY", "服务端金额不正确")
    payment_path = f"/api/payments/orders/{order['id']}"
    payment = request("POST", payment_path, {"paymentToken": "success"}, buyer, "pay-" + run)
    require(payment["status"] == "SUCCEEDED", "模拟支付没有成功")
    require(request("GET", f"/api/orders/{order['id']}", token=buyer)["status"] == "PAID", "支付返回成功但订单未落库为 PAID")
    require(request("POST", payment_path, {"paymentToken": "success"}, buyer, "pay-" + run)["paymentId"] == payment["paymentId"], "支付重试没有复用原结果")
    wait_until(lambda: request("GET", "/api/notifications", token=buyer),
        lambda rows: any(order["id"] in row["message"] for row in rows), 60, "付款通知（真实 RabbitMQ 消费）")
    refund_path = f"/api/payments/{payment['paymentId']}/refunds"
    refund = request("POST", refund_path, token=buyer, key="refund-" + run)
    require(refund["status"] == "SUCCEEDED", "模拟退款失败")
    require(request("POST", refund_path, token=buyer, key="refund-" + run)["refundId"] == refund["refundId"], "退款重试没有复用原结果")
    require(request("GET", f"/api/orders/{order['id']}", token=buyer)["status"] == "REFUNDED", "退款未落库")
    print(json.dumps({"status": "passed", "orderId": order["id"], "paymentId": payment["paymentId"],
        "refundId": refund["refundId"], "checks": ["register/login", "product/publication", "order/replay",
        "payment/replay", "persisted-state", "rabbitmq-notification", "refund/replay"]}, ensure_ascii=False))


if __name__ == "__main__":
    try: main()
    except (RuntimeError, URLError, TimeoutError, KeyError, ValueError) as error:
        print(f"Smoke failed: {error}", file=sys.stderr)
        raise SystemExit(1)
