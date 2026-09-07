#!/usr/bin/env python3
"""从工程目录调用仓库统一的学习引用检查，避免维护两套不同的校验规则。

作用：检查文档和源码引用的本地目标是否存在。
为什么：文件改名后需要及时发现断链；路径存在并不表示说明文字一定正确。
对应文档：mini-commerce/docs/LEARNING-READINESS.md 第 8 节。
"""
from pathlib import Path
import subprocess
import sys


def main() -> int:
    repo = Path(__file__).resolve().parents[2]
    result = subprocess.run(
        [sys.executable, str(repo / "tools/check_learning_references.py")],
        cwd=repo,
        check=False,
    )
    return result.returncode


if __name__ == "__main__":
    raise SystemExit(main())
