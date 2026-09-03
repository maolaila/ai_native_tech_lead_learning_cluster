from __future__ import annotations
import json,re,sys
from pathlib import Path
project=Path(__file__).resolve().parents[1];repo=project.parent
errors=[];refs=[]
for source in (project/"backend/src").rglob("*.java"):
    text=source.read_text(encoding="utf-8")
    for ref in re.findall(r"(?:00_start|0[1-9]_[\w]+|1[0-6]_[\w]+|13_ai_engineering_mcp|14_capstone)/[^\s、，。*]+?\.md",text):
        refs.append((source,ref))
        if not (repo/ref).exists():errors.append(f"{source.relative_to(repo)} -> missing {ref}")
map_path=project/"docs/generated/document-code-map.json"
if not map_path.exists():errors.append("missing docs/generated/document-code-map.json")
print(json.dumps({"references":len(refs),"errors":errors},ensure_ascii=False,indent=2));sys.exit(1 if errors else 0)
