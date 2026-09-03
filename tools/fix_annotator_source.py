#!/usr/bin/env python3
"""修复注释生成器的已知源码问题，并保持操作可重复执行。

这个小脚本只用于修复当前修复分支上的生成器本身。工作流随后会运行真正的
``annotate_learning_code.py``、Spotless 和测试；成功后，修复后的生成器也会一并提交。
"""

from pathlib import Path

path = Path(__file__).with_name("annotate_learning_code.py")
text = path.read_text(encoding="utf-8")
changed = False

# Python f-string 中，Javadoc 的大括号必须写成双大括号，否则会被当成 Python 表达式。
bad_f_string = 'f" * {module_name}模块的{title}：{@code {class_name}}。\\n"'
good_f_string = 'f" * {module_name}模块的{title}：{{@code {class_name}}}。\\n"'
if bad_f_string in text:
    text = text.replace(bad_f_string, good_f_string, 1)
    changed = True

# 旧逻辑遇到已有 Javadoc 就完全跳过，因此部分核心类虽然有说明，却没有“对应文档”。
# 新逻辑保留原说明，并把文档映射追加到已有 Javadoc 的末尾。
old_block = '''    between = text[insert_at : declaration.start()]
    if "/**" in between or "对应文档：" in text[: declaration.start()]:
        return text, False

    comment = class_javadoc(path, declaration.group("name"))
    return text[:insert_at] + "\\n\\n" + comment + text[insert_at:].lstrip("\\n"), True
'''

new_block = '''    between = text[insert_at : declaration.start()]
    if "对应文档：" in between:
        return text, False

    if "/**" in between and "*/" in between:
        module = detect_module(path)
        docs = MODULE_DOCS.get(module, MODULE_DOCS["shared"])
        docs_text = "、\\n * ".join(f"{{@code {doc}}}" for doc in docs)
        mapping = (
            "\\n *"
            "\\n * <p><strong>对应文档：</strong>\\n"
            f" * {docs_text}。</p>\\n "
        )
        close_at = insert_at + between.rfind("*/")
        return text[:close_at] + mapping + text[close_at:], True

    comment = class_javadoc(path, declaration.group("name"))
    return text[:insert_at] + "\\n\\n" + comment + text[insert_at:].lstrip("\\n"), True
'''

if old_block in text:
    text = text.replace(old_block, new_block, 1)
    changed = True
elif new_block not in text:
    raise SystemExit("expected add_class_javadoc source block was not found")

path.write_text(text, encoding="utf-8")
print("annotator source fixed" if changed else "annotator source already fixed")
