# 可执行实验材料

这里不是完整应用代码，而是用于搭建依赖、生成数据、复现数据库/消息/缓存问题的最小材料。

## 1. 启动基础设施

```bash
cd practice
cp .env.example .env
docker compose up -d postgres redis rabbitmq

docker compose ps
```

可选 Observability：

```bash
docker compose --profile observability up -d
```

端口默认：

| Service | Port |
|---|---:|
| PostgreSQL | 15432 |
| Redis | 16379 |
| RabbitMQ AMQP | 15672 |
| RabbitMQ Management | 15673 |
| Prometheus | 19090 |
| Grafana | 13000 |

## 2. 初始化 Schema

Compose 首次创建空 Volume 时会自动执行 `sql/01_schema.sql` 和 `sql/02_seed.sql`。

手动：

```bash
psql 'postgresql://commerce:commerce-local@localhost:15432/commerce' \
  -f sql/01_schema.sql
psql 'postgresql://commerce:commerce-local@localhost:15432/commerce' \
  -f sql/02_seed.sql
```

## 3. 生成大数据

```bash
psql "$DATABASE_URL" -v order_count=1000000 -f sql/03_generate_orders.sql
```

先用 100000 验证本机资源，再到 1000000。

## 4. 实验

- `sql/04_index_lab.sql`：执行计划和复合索引；
- `sql/05_atomic_inventory.sql`：条件更新；
- `sql/06_deadlock_lab.md`：两个 Session 复现死锁；
- `http/mini-commerce.http`：API 请求轮廓；
- `testing/order-test-matrix.md`：订单测试矩阵；
- `mcp/example-tool-spec.json`：Tool Contract 示例；
- `prometheus/prometheus.yml`：本地指标抓取样例。

## 5. 清理

```bash
docker compose down
```

保留数据 Volume。彻底删除：

```bash
docker compose down -v
```

后者会删除数据库数据，确认后执行。

## 6. 版本

`.env.example` 使用 Major Tag 作为学习基线；实际团队应固定经过验证的 Patch/Digest，并定期更新。
