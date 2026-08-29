# 隔离级别、MVCC 与死锁

> **所属模块：** 04 Database
> **本文用途：** 理解并发事务看到什么、为何读写能并行，以及死锁怎样检测和恢复。
> **前置知识：** 事务与锁
> **建议投入：** 阅读 5 小时，双会话实验 6 小时

---

## 一、隔离控制可见性

### Read Committed

每条语句看到开始时已提交的快照；同一事务两次 SELECT 可能不同。

### Repeatable Read

事务内快照更稳定；仍需理解 PostgreSQL 的具体语义和序列化冲突。

### Serializable

目标效果等价某种串行顺序；数据库可能中止冲突事务，应用必须重试。

最强不是无成本的默认选择。

## 二、异常

- Dirty Read：读未提交；PostgreSQL 不提供真正 Dirty Read；
- Non-repeatable Read：同一行两次读值不同；
- Phantom：同一条件两次结果集合不同。

不要只背通用表格，必须用 PostgreSQL 两会话实验。

## 三、MVCC

不同事务可看到不同版本，普通读取通常不阻塞普通更新。旧版本之后由 Vacuum 清理。

MVCC 不等于无锁：UPDATE、FOR UPDATE、DDL、Unique 和 Foreign Key 都会涉及锁。

## 四、长事务

长事务持锁、占连接、阻碍旧版本清理、造成表膨胀和 `idle in transaction`。不要开启事务后等待外部 API 或用户输入。

## 五、死锁

```text
A 锁 Row1 等 Row2
B 锁 Row2 等 Row1
```

PostgreSQL 检测后中止其中一个事务。成熟应用把部分死锁视为可恢复并发事件。

降低：固定顺序、缩短事务、合适索引、减少无关更新、有限重试。

重试整个事务，不只重试最后 SQL，因为此前读取和决定已可能过期。

## 六、DDL 锁

大表 ALTER、普通建索引可能获得强锁。本地 10ms 不代表生产安全。评估表大小、锁等待、Timeout、回填、停止条件和前滚策略。

## 七、实验

两个 psql 会话完成：

- Read Committed 两次读；
- `FOR UPDATE` 等待；
- 死锁；
- 死锁重试；
- 长事务；
- `pg_stat_activity` 查看等待和执行时长。
