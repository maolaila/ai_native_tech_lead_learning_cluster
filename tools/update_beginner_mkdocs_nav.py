#!/usr/bin/env python3
"""把后端小白学习资料加入 MkDocs 导航；脚本可重复执行。"""

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
PATH = REPO_ROOT / "mkdocs.yml"

BLOCK = '''  - "后端小白专用入口":
      - "后端零基础：从这里开始": "mini-commerce/docs/BEGINNER-START-HERE.md"
      - "一次创建订单请求完整走读": "mini-commerce/docs/REQUEST-TO-DATABASE-WALKTHROUGH.md"
      - "Spring 与 Java 注解小白词典": "mini-commerce/docs/SPRING-JAVA-ANNOTATIONS.md"
      - "后端专有名词通俗词典": "mini-commerce/docs/BACKEND-TERMS-PLAIN-CHINESE.md"
      - "Java 后端阅读语法速查": "mini-commerce/docs/JAVA-SYNTAX-FOR-BACKEND-BEGINNERS.md"
      - "Spring 配置从零开始": "mini-commerce/docs/CONFIGURATION-FROM-ZERO.md"
      - "ADHD 友好的学习计划": "mini-commerce/docs/ADHD-FOCUSED-LEARNING-PLAN.md"
      - "后端小白常见问题": "mini-commerce/docs/BEGINNER-FAQ.md"
'''


def main() -> None:
    text = PATH.read_text(encoding="utf-8")
    if '  - "后端小白专用入口":' in text:
        print("beginner nav already exists")
        return
    marker = "nav:\n"
    if marker not in text:
        raise SystemExit("mkdocs.yml does not contain nav section")
    PATH.write_text(text.replace(marker, marker + BLOCK, 1), encoding="utf-8")
    print("beginner nav inserted")


if __name__ == "__main__":
    main()
