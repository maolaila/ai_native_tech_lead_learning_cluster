"""整理交付导航与中文说明；不修改工作流，不改历史迁移，不自动合并 main。"""
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]

def replace(name, old, new):
    p = ROOT / name
    text = p.read_text(encoding="utf-8")
    if old not in text:
        raise ValueError(f"原文变化，请检查 {name}")
    p.write_text(text.replace(old, new), encoding="utf-8")

for name in ("README.md", "mini-commerce/README.md"):
    prefix = "mini-commerce/" if name == "README.md" else ""
    p = ROOT / name
    text = p.read_text(encoding="utf-8")
    pos = text.index("\n")
    text = text[:pos+1] + f"\n> 正式学习先读 [启动与学习范围]({prefix}docs/LEARNING-READINESS.md)，修订与证据见 [开学前检查记录]({prefix}docs/PRE-STUDY-REVIEW.md)。日常学习使用 main；示例中的令牌和 ID 需替换为真实响应值。\n" + text[pos+1:]
    p.write_text(text, encoding="utf-8")
replace("mini-commerce/README.md", "可直接执行的 HTTP 请求集", "按步骤填写变量后执行的 HTTP 请求集")
replace("mkdocs.yml", '      - "正式学习说明与验收范围": "mini-commerce/docs/LEARNING-READINESS.md"', '      - "正式学习说明与验收范围": "mini-commerce/docs/LEARNING-READINESS.md"\n      - "开学前修订与验证证据": "mini-commerce/docs/PRE-STUDY-REVIEW.md"')
replace("SUMMARY.md", "- [正式学习说明与验收范围](mini-commerce/docs/LEARNING-READINESS.md)", "- [正式学习说明与验收范围](mini-commerce/docs/LEARNING-READINESS.md)\n- [开学前修订与验证证据](mini-commerce/docs/PRE-STUDY-REVIEW.md)")
p = ROOT / "mini-commerce/.gitignore"
p.write_text(p.read_text() + "\n# 数据备份可能含账号与业务数据，不能提交到仓库。\nbackups/\n*.dump\n*.partial\n", encoding="utf-8")
for p in (ROOT / "mini-commerce").glob("CI-FAILURE-*.md"):
    p.write_text("> 历史失败日志：用于记录早期修复过程，不是当前 main 的验收结论。当前范围和版本证据请阅读 docs/PRE-STUDY-REVIEW.md。\n\n" + p.read_text(), encoding="utf-8")
p = ROOT / "mini-commerce/docs/LEARNING-READINESS.md"
p.write_text(p.read_text() + "\n修订清单、已验证的源码版本与备份演练见 [开学前修订记录](PRE-STUDY-REVIEW.md)。\n\n下载 ZIP 后可以直接阅读 Markdown 和运行 Compose。文档站构建脚本使用 Git 的文件清单，请在 git clone 得到的工作目录中运行；不要把 ZIP 解压目录当成已经带有 Git 历史的仓库。\n", encoding="utf-8")
replace("mini-commerce/backend/src/main/java/com/example/minicommerce/shared/transaction/AfterCommitExecutor.java", " * 仅把可重试/可补偿的非核心动作放到提交后。关键可靠异步动作仍需 Outbox，不能只依赖 afterCommit 回调。", " * 数据库确认提交成功以后，再执行一小段辅助动作，例如增加监控计数。\n *\n * <p>大白话：订单真正写好了，才在计数器上加一；事务回滚就不加。\n * 这里不会新开线程，也不是消息队列；回调通常仍在提交事务的线程里执行。\n *\n * <p>为什么不能靠它发送关键消息：提交后如果进程突然退出，回调可能没有执行，也没有自动补发记录。\n * 需要可靠重试的通知仍应写 Outbox。这里也不负责回滚已经提交的数据库。")
replace("mini-commerce/backend/src/main/java/com/example/minicommerce/shared/transaction/AfterCommitExecutor.java", "    public void run(Runnable action) {", "    /** action 是一段稍后执行的代码；有事务时等提交成功，没有事务时立即执行。 */\n    public void run(Runnable action) {")
print("交付导航与中文说明已整理；完整测试随后执行，不预写通过结论。")
