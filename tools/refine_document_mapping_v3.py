from __future__ import annotations

import json
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
MAP_JSON = REPO / "mini-commerce/docs/generated/document-code-map.json"
MAP_MD = REPO / "mini-commerce/docs/generated/document-code-map.md"
CATALOG = REPO / "mini-commerce/docs/generated/source-catalog.json"

data = json.loads(MAP_JSON.read_text(encoding="utf-8"))
entries = data["entries"]

rules = [
    (("反向代理", "tls", "502", "504"), ["mini-commerce/infra/nginx/nginx.conf", "mini-commerce/compose.yaml"]),
    (("pipeline", "githubactions", "jenkins", "ci/cd", "质量门禁"), [".github/workflows/mini-commerce-ci.yml", "mini-commerce/Jenkinsfile"]),
    (("api", "契约", "错误码", "validation"), ["mini-commerce/api/openapi.yaml", "mini-commerce/api/mini-commerce.http"]),
    (("对象级权限", "rbac", "越权"), [
        "mini-commerce/backend/src/main/java/com/example/minicommerce/order/application/OrderQueryService.java",
        "mini-commerce/backend/src/test/java/com/example/minicommerce/order/OrderObjectAuthorizationIT.java",
    ]),
    (("支付", "webhook", "重复回调"), ["mini-commerce/backend/src/main/java/com/example/minicommerce/payment"]),
    (("退款",), ["mini-commerce/backend/src/main/java/com/example/minicommerce/refund"]),
    (("备份", "恢复", "rpo", "rto"), ["mini-commerce/scripts/backup.sh", "mini-commerce/scripts/restore-test.sh"]),
    (("故障", "incident", "排障"), ["mini-commerce/labs/failure-matrix.md", "mini-commerce/docs/runbooks/incident-response.md"]),
    (("openapi",), ["mini-commerce/api/openapi.yaml"]),
]

for entry in entries:
    haystack = f"{entry['source']} {entry['title']}".lower()
    targets = list(entry.get("codeTargets", []))
    for keywords, additions in rules:
        if any(keyword.lower() in haystack for keyword in keywords):
            targets.extend(additions)
    entry["codeTargets"] = list(dict.fromkeys(targets))[:8]

MAP_JSON.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
CATALOG.write_text(json.dumps(entries, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

rows = [
    "# 文档章节与代码逐项映射",
    "",
    "> 此文件由仓库脚本从实际 Markdown H1～H3 标题生成，并在最终工程资产落地后精化。",
    "> 代码仍按真实业务边界组织；映射用于从知识点跳转到实现、测试、配置或故障实验。",
    "",
    f"共映射 **{len(entries)}** 个章节。机器可读版：`document-code-map.json`。",
    "",
    "| Source ID | 文档与章节 | 对应工程位置 |",
    "|---|---|---|",
]
for entry in entries:
    title = str(entry["title"]).replace("|", "\\|")
    targets = "<br>".join(f"`{target}`" for target in entry["codeTargets"])
    rows.append(f"| `{entry['sourceId']}` | `{entry['source']}:{entry['line']}`<br>{title} | {targets} |")
MAP_MD.write_text("\n".join(rows) + "\n", encoding="utf-8")
print(json.dumps({"status": "mapping-refined", "entries": len(entries)}, ensure_ascii=False))
