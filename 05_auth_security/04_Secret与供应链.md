# Secret、依赖与软件供应链

> **所属模块：** 05 Security
> **本文用途：** 防止凭证、第三方依赖和 CI 权限成为攻击入口。
> **前置知识：** 应用安全
> **建议投入：** 阅读 3 小时，配置 4 小时

---

## 一、Secret

数据库密码、API Key、私钥、OAuth Secret、签名 Key、云凭证、Deploy Token。

不能硬编码、提交 Git、写日志、放前端 Bundle、截图或让 MCP 任意读取。

## 二、`.env`

适合本地便利，不是生产 Secret Manager。生产需要加密、权限、审计、轮换和环境隔离。

## 三、泄露响应

立即撤销/轮换、查使用日志、评估范围、清理公开历史、通知、加扫描和复盘。删除当前 Git 文件不够。

## 四、依赖

风险：CVE、维护停滞、包接管、恶意版本、Transitive、安装脚本。

- Lockfile/Dependency Management；
- 安全更新与普通更新分开；
- CI 测试；
- SCA、Secret、Image、License 扫描；
- SBOM；
- 新依赖说明用途、维护状态和替代方案。

## 五、CI 权限

PR 代码不可信：默认无生产 Secret；固定第三方 Action 版本；环境审批；最小 `permissions`；隔离 Runner；未审代码不能执行高权限步骤。

## 六、Artifact

一次 Build 生成不可变 Artifact/Image，在 Staging 和 Production 提升同一 Digest。不要生产服务器重新从不确定依赖 Build。

## 七、AI 风险

AI 可能推荐不存在/恶意相似包、打印 Token、关闭校验、新增过时算法。所有依赖和权限变更必须人工 Review。
