"""保留行号，跳过 Java 注释与字面量后查找真实注解；不是完整 Java 语法解析器。"""
from __future__ import annotations

import re
from typing import Iterator

# 先匹配注释、文本块、字符串和字符，避免把其中的 @Service 算成真实注解。
_NON_CODE = re.compile(
    r'//[^\n]*|/\*[\s\S]*?\*/|"""[\s\S]*?"""|"(?:\\.|[^"\\])*"|\'(?:\\.|[^\'\\])*\''
)
_ANNOTATION = re.compile(r'@(?:[A-Za-z_$][\w$]*\.)*([A-Z][\w$]*)\b')


def mask_non_code(text: str) -> str:
    """以空格替换非代码文字但保留换行，让结果仍对应原始文件行号。"""
    return _NON_CODE.sub(lambda match: re.sub(r'[^\n]', ' ', match.group()), text)


def annotations(text: str) -> Iterator[tuple[str, int]]:
    """返回（注解简单名称，原文件行号）；也识别完整包名的注解写法。"""
    for number, line in enumerate(mask_non_code(text).splitlines(), 1):
        for match in _ANNOTATION.finditer(line):
            yield match.group(1), number
