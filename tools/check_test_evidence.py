"""读取 Maven 实际 XML；CI 不允许“没有执行集成测试”被当作全部通过。

本地没有 Docker 时可以只读源码和运行单元测试，但正式验收必须真实运行 PostgreSQL 测试。
"""
from pathlib import Path
import json
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
TARGET = ROOT / "mini-commerce/backend/target"
EXPECTED = {"com.example.minicommerce.BusinessSafetyIT", "com.example.minicommerce.LearningReadinessIT", "com.example.minicommerce.inventory.InventoryConcurrencyIT", "com.example.minicommerce.order.CreateOrderIT"}


def main() -> None:
    totals = dict(tests=0, failures=0, errors=0, skipped=0)
    integration_suites = set()
    for folder in ("surefire-reports", "failsafe-reports"):
        reports = sorted((TARGET / folder).glob("TEST-*.xml"))
        if not reports:
            raise AssertionError("没有取得测试 XML：" + folder)
        for path in reports:
            suite = ET.parse(path).getroot()
            for key in totals:
                totals[key] += int(suite.attrib.get(key, "0"))
            if folder == "failsafe-reports" and int(suite.attrib.get("tests", "0")) > 0:
                integration_suites.add(suite.attrib["name"])
    if not EXPECTED.issubset(integration_suites):
        raise AssertionError("关键集成测试未执行：" + str(EXPECTED - integration_suites))
    if not totals["tests"] or any(totals[key] for key in ("failures", "errors", "skipped")):
        raise AssertionError("验收包含失败、错误、跳过或零测试：" + str(totals))
    print(json.dumps({"status": "passed", **totals, "integrationSuites": sorted(integration_suites)}))


if __name__ == "__main__":
    main()
