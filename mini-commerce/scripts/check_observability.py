"""用真实 HTTP 验证指标导出和 Prometheus 抓取，而不是只检查配置中写了指标名。

对应文档：mini-commerce/docs/observability.md。
只用于本地学习；需先运行 Smoke 创建一笔订单，并启动 observability Profile。
"""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import time
from urllib.parse import urlencode, urlsplit
from urllib.request import urlopen

METRIC = "commerce_orders_creation_total"


def local_url(value: str) -> str:
    """验收脚本只检查本机端口，避免误指向生产。"""
    parts = urlsplit(value)
    if parts.scheme != "http" or parts.hostname not in {
        "127.0.0.1",
        "localhost",
        "::1",
    }:
        raise ValueError("该脚本只接受本地 HTTP 地址")
    return value.rstrip("/")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, help="可选：保存不含账户数据的验证摘要")
    args = parser.parse_args()
    backend = local_url(os.environ.get("BASE_URL", "http://127.0.0.1:18080"))
    prometheus = local_url(os.environ.get("PROMETHEUS_URL", "http://127.0.0.1:19090"))
    with urlopen(backend + "/actuator/prometheus", timeout=5) as response:
        text = response.read().decode("utf-8")
    samples = [
        line
        for line in text.splitlines()
        if line.startswith(METRIC + " ") or line.startswith(METRIC + "{")
    ]
    if not samples or not any(float(line.split()[1]) >= 1 for line in samples):
        raise AssertionError("后端没有导出正数的订单计数；先运行 Smoke，并核对指标名称")

    # up=1 只证明抓取成功；还要查业务计数，避免网页可打开但业务指标为空。
    last = None
    for _ in range(30):
        try:
            results = {}
            for query in ['up{job="mini-commerce"}', METRIC + '{job="mini-commerce"}']:
                with urlopen(
                    prometheus + "/api/v1/query?" + urlencode({"query": query}),
                    timeout=5,
                ) as response:
                    data = json.load(response)
                if data.get("status") != "success":
                    raise ValueError("Prometheus 查询失败")
                results[query] = data["data"]["result"]
            if all(
                any(float(sample["value"][1]) >= 1 for sample in values)
                for values in results.values()
            ):
                report = {
                    "status": "passed",
                    "exporterMetric": METRIC,
                    "prometheusJob": "mini-commerce",
                    "checks": [
                        "backend-exporter",
                        "prometheus-up",
                        "prometheus-order-counter",
                    ],
                }
                if args.output:
                    args.output.parent.mkdir(parents=True, exist_ok=True)
                    args.output.write_text(
                        json.dumps(report, ensure_ascii=False, indent=2) + "\n",
                        encoding="utf-8",
                    )
                print(json.dumps(report, ensure_ascii=False))
                return
        except (OSError, ValueError, KeyError) as exc:
            last = str(exc)
        time.sleep(2)
    raise AssertionError("Prometheus 未抓到后端健康状态和业务计数：" + str(last))


if __name__ == "__main__":
    main()
