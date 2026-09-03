from __future__ import annotations
import json,os,subprocess,time
from datetime import datetime,timezone
from pathlib import Path
from typing import Any
import psycopg
from .security import redact,safe_resolve,untrusted_excerpt,validate_readonly_sql

ROOT=Path(os.getenv("REPOSITORY_ROOT",Path(__file__).resolve().parents[4])).resolve()
AUDIT=Path(os.getenv("MCP_AUDIT_PATH",ROOT/"mini-commerce"/"mcp-audit"/"audit.jsonl"))
SUITES={"backend-unit":["mvn","-B","-DskipITs","test"],"backend-all":["mvn","-B","verify"],"mcp":["python","-m","pytest","-q"]}

def audit(tool:str,args:dict[str,Any],status:str,duration_ms:int)->None:
    AUDIT.parent.mkdir(parents=True,exist_ok=True)
    row={"observedAt":datetime.now(timezone.utc).isoformat(),"actor":"mcp-client","tool":tool,"arguments":redact(args),"status":status,"durationMs":duration_ms}
    with AUDIT.open("a",encoding="utf-8") as f:f.write(json.dumps(row,ensure_ascii=False)+"\n")

def search_docs(query:str,limit:int=8)->dict[str,Any]:
    started=time.monotonic();limit=max(1,min(limit,20));terms=[t.lower() for t in query.split() if len(t)>1];results=[]
    for path in ROOT.rglob("*.md"):
        if any(part in {".git","target","node_modules"} for part in path.parts):continue
        text=path.read_text(encoding="utf-8",errors="ignore")
        score=sum(text.lower().count(term) for term in terms)
        if score:
            positions=[text.lower().find(term) for term in terms if text.lower().find(term)>=0];pos=min(positions) if positions else 0
            excerpt=text[max(0,pos-300):pos+1200].replace("\x00","")
            results.append((score,{"source":str(path.relative_to(ROOT)),"score":score,"excerpt":untrusted_excerpt(excerpt)}))
    data=[item for _,item in sorted(results,key=lambda x:(-x[0],x[1]["source"]))[:limit]]
    audit("search_learning_docs",{"query":query,"limit":limit},"ok",int((time.monotonic()-started)*1000))
    return {"status":"ok","data":data,"truncated":len(results)>limit,"sourceRevision":os.getenv("GIT_COMMIT","workspace"),"observedAt":datetime.now(timezone.utc).isoformat()}

def read_runbook(relative_path:str)->dict[str,Any]:
    started=time.monotonic();path=safe_resolve(ROOT,relative_path)
    allowed=(ROOT/"mini-commerce"/"docs"/"runbooks").resolve()
    try:path.relative_to(allowed)
    except ValueError as exc:raise ValueError("PERMISSION_DENIED: only runbooks are readable by this tool") from exc
    data=untrusted_excerpt(path.read_text(encoding="utf-8"))
    audit("read_runbook",{"path":relative_path},"ok",int((time.monotonic()-started)*1000));return {"status":"ok","source":str(path.relative_to(ROOT)),"data":data}

def database_schema()->dict[str,Any]:
    started=time.monotonic();url=os.getenv("DATABASE_READONLY_URL")
    if not url:
        migration=safe_resolve(ROOT,"mini-commerce/backend/src/main/resources/db/migration/V001__baseline.sql")
        result={"mode":"migration","source":str(migration.relative_to(ROOT)),"ddl":migration.read_text(encoding="utf-8")[:30000]}
    else:
        with psycopg.connect(url,options="-c default_transaction_read_only=on -c statement_timeout=2000") as conn:
            rows=conn.execute("select table_name,column_name,data_type,is_nullable from information_schema.columns where table_schema='public' order by table_name,ordinal_position").fetchall()
        result={"mode":"live-readonly","columns":[{"table":r[0],"column":r[1],"type":r[2],"nullable":r[3]} for r in rows[:2000]]}
    audit("get_database_schema",{},"ok",int((time.monotonic()-started)*1000));return {"status":"ok","data":result,"truncated":False}

def explain_readonly(sql:str)->dict[str,Any]:
    started=time.monotonic();safe=validate_readonly_sql(sql);url=os.getenv("DATABASE_READONLY_URL")
    if not url:raise RuntimeError("DEPENDENCY_UNAVAILABLE: DATABASE_READONLY_URL is not configured")
    with psycopg.connect(url,options="-c default_transaction_read_only=on -c statement_timeout=2000") as conn:
        plan=conn.execute("EXPLAIN (FORMAT JSON) "+safe).fetchone()[0]
    audit("explain_readonly_query",{"sql":safe},"ok",int((time.monotonic()-started)*1000));return {"status":"ok","data":plan,"analyze":False,"note":"生产默认不执行 EXPLAIN ANALYZE，避免真实执行副作用或高成本查询"}

def run_suite(name:str)->dict[str,Any]:
    started=time.monotonic()
    if name not in SUITES:raise ValueError("INVALID_ARGUMENT: suite is not allowlisted")
    cwd=ROOT/"mini-commerce"/("mcp-server" if name=="mcp" else "backend")
    completed=subprocess.run(SUITES[name],cwd=cwd,text=True,capture_output=True,timeout=600,check=False,shell=False)
    output=(completed.stdout+"\n"+completed.stderr)[-20000:]
    status="passed" if completed.returncode==0 else "failed";audit("run_test_suite",{"name":name},status,int((time.monotonic()-started)*1000))
    return {"status":status,"exitCode":completed.returncode,"command":SUITES[name],"output":output,"truncated":len(completed.stdout)+len(completed.stderr)>20000}
