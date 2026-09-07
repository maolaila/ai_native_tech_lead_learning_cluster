#!/usr/bin/env python3
"""把 Git 跟踪的文档和源码复制到隔离快照构建；不公开未跟踪日志与 .env。"""
from __future__ import annotations
import argparse
import json
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SOURCE_CONFIG = REPO_ROOT / "mkdocs.yml"
DEFAULT_OUTPUT = REPO_ROOT.parent / f"{REPO_ROOT.name}-site"


def validate_output(output: Path, repo: Path = REPO_ROOT) -> Path:
    output, repo = output.resolve(), repo.resolve()
    if output == Path(output.anchor) or output == repo or output in repo.parents or repo in output.parents:
        raise ValueError("输出不能是文件系统根、仓库、仓库祖先或仓库内部目录")
    marker = output.parent / (output.name + ".learning-site-owner")
    if output.exists() and (not output.is_dir() or any(output.iterdir())):
        if not marker.is_file() or marker.read_text(encoding="utf-8") != str(repo):
            raise ValueError("拒绝清理非本工具拥有的非空目录；请使用新的 --output 路径，不要删除未知文件")
    return marker


def snapshot(destination: Path) -> None:
    tracked = subprocess.check_output(["git", "ls-files", "-z"], cwd=REPO_ROOT).decode("utf-8").split("\0")
    for name in tracked:
        if not name: continue
        path = REPO_ROOT / name
        if not path.is_file() or path.is_symlink(): continue
        if path.name == ".env" or any(part in {".git", "target", "node_modules", "mcp-audit", "__pycache__", ".terraform"} for part in path.parts): continue
        target = destination / name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(path, target)


def runtime_config(docs: Path, output: Path) -> str:
    text = SOURCE_CONFIG.read_text(encoding="utf-8")
    for name, path in (("docs_dir", docs), ("site_dir", output)):
        text, count = re.subn(rf"(?m)^{name}:\s*.*$", lambda _: f"{name}: {json.dumps(str(path))}", text, count=1)
        if count != 1: raise ValueError(f"mkdocs.yml 必须包含一行 {name}")
    return text


def main() -> int:
    parser = argparse.ArgumentParser(description="隔离快照构建或预览学习文档；新增文件先 git add，修改后重启预览")
    parser.add_argument("--serve", action="store_true")
    parser.add_argument("--strict", action="store_true")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--address", default="127.0.0.1:8000")
    args = parser.parse_args()
    output = args.output.resolve()
    marker = None if args.serve else validate_output(output)
    with tempfile.TemporaryDirectory(prefix="learning-docs-") as folder:
        root = Path(folder)
        docs, site = root / "docs", root / "site"
        docs.mkdir()
        snapshot(docs)
        config = root / "mkdocs.runtime.yml"
        config.write_text(runtime_config(docs, site), encoding="utf-8")
        command = [sys.executable, "-m", "mkdocs", "serve" if args.serve else "build", "-f", str(config)]
        if args.strict: command.append("--strict")
        if args.serve:
            command.extend(["--dev-addr", args.address])
            print("本地快照预览；修改后请重启，新增文件请先 git add。", flush=True)
        result = subprocess.run(command, cwd=REPO_ROOT, check=False).returncode
        if result == 0 and not args.serve:
            # 构建成功且输出目录属于本工具时才替换，不让 MkDocs 清空任意用户目录。
            validate_output(output)
            if output.exists(): shutil.rmtree(output)
            output.parent.mkdir(parents=True, exist_ok=True)
            shutil.copytree(site, output)
            marker.write_text(str(REPO_ROOT.resolve()), encoding="utf-8")
            print(f"站点已生成：{output}")
        return result


if __name__ == "__main__":
    try: raise SystemExit(main())
    except ValueError as error: raise SystemExit(str(error)) from None
