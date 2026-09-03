#!/usr/bin/env python3
"""使用临时 MkDocs 配置构建或预览整仓库文档。

原知识库的 Markdown 分散在仓库根目录多个模块中，因此 docs_dir 需要指向仓库根目录。
MkDocs 1.6 不允许配置文件本身位于 docs_dir 中，也不允许 site_dir 位于 docs_dir 内。
本脚本把运行时配置放到系统临时目录，并把站点输出到仓库外部，避免复制自身。
"""

from __future__ import annotations

import argparse
import re
import subprocess
import tempfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SOURCE_CONFIG = REPO_ROOT / "mkdocs.yml"
DEFAULT_OUTPUT = REPO_ROOT.parent / f"{REPO_ROOT.name}-site"


def runtime_config(output: Path) -> str:
    text = SOURCE_CONFIG.read_text(encoding="utf-8")
    docs_dir = REPO_ROOT.resolve().as_posix()
    site_dir = output.resolve().as_posix()

    text, docs_count = re.subn(
        r"(?m)^docs_dir:\s*.*$",
        f'docs_dir: "{docs_dir}"',
        text,
        count=1,
    )
    text, site_count = re.subn(
        r"(?m)^site_dir:\s*.*$",
        f'site_dir: "{site_dir}"',
        text,
        count=1,
    )
    if docs_count != 1 or site_count != 1:
        raise SystemExit("mkdocs.yml 必须各包含一行 docs_dir 和 site_dir")
    return text


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="构建或预览 AI-Native Tech Lead 学习文档站"
    )
    parser.add_argument(
        "--serve",
        action="store_true",
        help="启动本地预览服务器，而不是只构建静态站点",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="把 MkDocs 警告当作失败，CI 应启用",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT,
        help=f"站点输出目录，必须在仓库外；默认 {DEFAULT_OUTPUT}",
    )
    parser.add_argument(
        "--address",
        default="127.0.0.1:8000",
        help="--serve 时监听地址，默认 127.0.0.1:8000",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    output = args.output.resolve()
    try:
        output.relative_to(REPO_ROOT.resolve())
    except ValueError:
        pass
    else:
        raise SystemExit(
            "站点输出目录不能放在仓库内部，否则 MkDocs 会把输出再次复制进自己"
        )

    output.parent.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory(prefix="ai-native-mkdocs-") as temp_dir:
        config_path = Path(temp_dir) / "mkdocs.runtime.yml"
        config_path.write_text(runtime_config(output), encoding="utf-8")

        command = ["mkdocs", "serve" if args.serve else "build", "-f", str(config_path)]
        if args.strict:
            command.append("--strict")
        if args.serve:
            command.extend(["--dev-addr", args.address])

        print("执行：", " ".join(command))
        print("文档源：", REPO_ROOT)
        print("站点输出：", output)
        return subprocess.run(command, cwd=REPO_ROOT, check=False).returncode


if __name__ == "__main__":
    raise SystemExit(main())
