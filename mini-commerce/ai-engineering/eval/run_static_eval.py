from __future__ import annotations
import json,re,sys
from pathlib import Path
root=Path(__file__).resolve().parents[2]
checks=[]
def check(name,condition,evidence):checks.append({"name":name,"passed":bool(condition),"evidence":evidence})
java="\n".join(p.read_text(encoding="utf-8") for p in (root/"backend/src/main/java").rglob("*.java"))
check("订单请求不接收客户端总价","totalAmount" not in (root/"backend/src/main/java/com/example/minicommerce/order/api/OrderDtos.java").read_text(),"OrderDtos")
check("条件库存更新","available>=:qty" in java,"InventoryRepository")
check("Outbox 同工程存在","outbox_events" in (root/"backend/src/main/resources/db/migration/V001__baseline.sql").read_text(),"V001")
check("MCP 拒绝 DDL","write or DDL keyword" in (root/"mcp-server/src/mini_commerce_mcp/security.py").read_text(),"security.py")
print(json.dumps({"passed":all(x["passed"] for x in checks),"checks":checks},ensure_ascii=False,indent=2))
sys.exit(0 if all(x["passed"] for x in checks) else 1)
