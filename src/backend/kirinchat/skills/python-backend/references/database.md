# 数据库与 ORM 知识点

## SQLAlchemy 核心
- Engine → Connection → Session
- ORM 模型定义（Declarative Base）
- 关系映射：一对多、多对多、一对一
- 懒加载 vs 预加载（selectinload/joinedload）

## SQL 优化
- 索引类型：B-Tree/Hash/GiST/GIN
- EXPLAIN ANALYZE 分析查询计划
- 慢查询优化：覆盖索引、避免 SELECT *
- N+1 查询问题及解决

## 数据库设计
- 范式化 vs 反范式化
- 分库分表策略
- 读写分离
- 连接池配置

## 事务与并发
- ACID 特性
- 隔离级别：读未提交/读已提交/可重复读/串行化
- 乐观锁 vs 悲观锁
- 死锁检测与预防

## PostgreSQL 特性
- JSONB 类型
- 数组类型
- 窗口函数
- CTE（公共表表达式）
- pgvector 向量存储
