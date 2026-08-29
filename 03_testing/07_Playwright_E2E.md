# Playwright E2E

> **所属模块：** 03 Testing
> **本文用途：** 自动验证真实浏览器、前端、后端和数据库的核心用户路径。
> **前置知识：** 前后端可运行
> **建议投入：** 阅读 4 小时，编码 8 小时

---

## 一、E2E 的职责

高价值：登录、商品、购物车、下单、权限、后台核心流程。

不适合覆盖所有字段组合，因为慢、环境复杂、失败定位成本高。

## 二、示例

```ts
import { test, expect } from '@playwright/test'

test('用户完成下单', async ({ page }) => {
  await page.goto('/login')
  await page.getByLabel('邮箱').fill('alice@example.com')
  await page.getByLabel('密码').fill('password')
  await page.getByRole('button', { name: '登录' }).click()
  await page.getByRole('link', { name: '商品' }).click()
  await page.getByRole('button', { name: '加入购物车' }).first().click()
  await page.getByRole('link', { name: '购物车' }).click()
  await page.getByRole('button', { name: '提交订单' }).click()
  await expect(page.getByText('订单创建成功')).toBeVisible()
})
```

## 三、Locator

优先 Role/Label/Text；避免 `div:nth-child(3)`。稳定 Locator 也推动可访问性。

## 四、Web-first Assertion

```ts
await expect(locator).toBeVisible()
```

自动重试真实条件。不要 `waitForTimeout`。

## 五、隔离

每测试独立 Browser Context 和测试数据；不依赖顺序；使用唯一用户。可复用登录 Storage State，但至少保留一条真实登录测试。

## 六、Fixture 与 Page Object

Fixture 提供 authenticatedPage、testUser、apiClient；Page Object 封装稳定页面操作。不要把所有断言隐藏进巨型对象。

## 七、数据准备

测试订单详情页面可以 API 准备订单；测试完整下单必须通过 UI。根据测试目标决定，不必所有准备都走 UI。

## 八、失败证据

配置 Trace、Screenshot、Video；CI 失败用 Trace Viewer 看 DOM、Network、Console、时间线。

## 九、Flaky 来源

固定 Sleep、共享数据、动画、异步未等待、外部真实服务、不稳定 Selector、时区、资源不足。

Retry 不是修复；它只能缓解和收集证据。

## 十、Smoke

发布后少量快速路径：首页、登录、商品列表、下单、管理员入口。完整 Regression 可在合并或夜间运行。
