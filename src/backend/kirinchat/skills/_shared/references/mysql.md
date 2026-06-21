# MySQL 核心知识点

## 索引

### B+ 树
- B+ 树结构特点：多路平衡、叶子节点链表、非叶子节点只存索引
- 为什么选择 B+ 树而非 B 树、红黑树、Hash
- 聚簇索引 vs 非聚簇索引（二级索引）
- 覆盖索引与回表查询

### 索引优化
- 最左前缀原则
- 索引失效的常见情况：函数操作、隐式转换、OR 条件、LIKE 以通配符开头
- 联合索引的设计策略
- EXPLAIN 执行计划：type、key、rows、Extra

## 事务

### ACID
- 原子性（Atomicity）：undo log 实现
- 一致性（Consistency）：由其他三个特性共同保证
- 隔离性（Isolation）：锁和 MVCC 实现
- 持久性（Durability）：redo log 实现

### 隔离级别
- READ UNCOMMITTED：脏读
- READ COMMITTED：不可重复读（Oracle 默认）
- REPEATABLE READ：幻读（MySQL 默认，InnoDB 通过 MVCC + 间隙锁解决部分幻读）
- SERIALIZABLE：串行化
- MVCC 实现原理：undo log 版本链、ReadView

## 锁

### 行锁
- Record Lock（记录锁）
- Gap Lock（间隙锁）
- Next-Key Lock（临键锁）

### 表锁
- 意向锁：意向共享锁（IS）、意向排他锁（IX）
- MDL 锁（元数据锁）

### 死锁
- 死锁产生条件：互斥、持有并等待、不可剥夺、循环等待
- 死锁检测与处理
- 避免死锁的策略

## 性能优化

### 慢查询
- 慢查询日志配置
- EXPLAIN 分析
- Profile 分析
- 常见优化手段：索引优化、SQL 改写、表结构优化

### 分库分表
- 垂直拆分：按业务拆分
- 水平拆分：按规则拆分数据
- 分片策略：范围分片、Hash 分片
- 分布式事务问题：XA、TCC、最终一致性
- 常用中间件：ShardingSphere、MyCat

### 其他
- 读写分离：主从复制原理、延迟问题
- 连接池配置与调优
- binlog、redo log、undo log 的区别与作用
