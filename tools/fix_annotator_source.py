#!/usr/bin/env python3
"""一次性修复注释生成器中的 Javadoc 大括号转义，并保持脚本可重复执行。"""

from pathlib import Path

path = Path(__file__).with_name("annotate_learning_code.py")
text = path.read_text(encoding="utf-8")
bad = 'f" * {module_name}模块的{title}：{@code {class_name}}。\\n"'
good = 'f" * {module_name}模块的{title}：{{@code {class_name}}}。\\n"'

if bad in text:
    path.write_text(text.replace(bad, good, 1), encoding="utf-8")
    print("annotator source fixed")
elif good in text:
    print("annotator source already fixed")
else:
    raise SystemExit("expected annotator source line was not found")
