# Redis 核心知识点

## 数据结构

### String
- 底层实现：SDS（Simple Dynamic String）
- 常用命令：SET、GET、INCR、DECR、MSET、MGET
- 应用场景：计数器、分布式 Session、缓存

### Hash
- 底层实现：ziplist 或 hashtable
- 常用命令：HSET、HGET、HGETALL、HINCRBY
- 应用场景：存储对象属性

### List
- 底层实现：quicklist（ziplist + 链表）
- 常用命令：LPUSH、RPUSH、LPOP、RPOP、LRANGE
- 应用场景：消息队列、最新列表

### Set
- 底层实现：intset 或 hashtable
- 常用命令：SADD、SREM、SMEMBERS、SINTER、SUNION
- 应用场景：去重、共同关注、抽奖

### Sorted Set
- 底层实现：ziplist 或 skiplist + hashtable
- 常用命令：ZADD、ZSCORE、ZRANGE、ZRANGEBYSCORE
- 应用场景：排行榜、延迟队列

## 持久化

### RDB
- 原理：定时快照，fork 子进程生成 dump.rdb
- 触发方式：save、bgsave、自动触发
- 优缺点：恢复快但可能丢失数据

### AOF
- 原理：追加写入命令日志
- 同步策略：always、everysec、no
- AOF 重写：减少文件体积
- 优缺点：数据安全但文件较大

### 混合持久化
- RDB + AOF 结合方案
- Redis 4.0+ 支持

## 高可用

### 主从复制
- 全量复制与增量复制
- 复制积压缓冲区
- 读写分离架构

### 哨兵（Sentinel）
- 故障检测：主观下线与客观下线
- leader 选举
- 自动故障转移

### 集群（Cluster）
- 数据分片：16384 个槽位（slot）
- 节点通信：Gossip 协议
- 集群扩缩容
- 集群中的请求路由

## 应用场景

### 缓存
- 缓存穿透：布隆过滤器、缓存空值
- 缓存击穿：互斥锁、热点数据永不过期
- 缓存雪崩：随机过期时间、多级缓存
- 缓存更新策略：Cache Aside、Read/Write Through、Write Behind

### 分布式锁
- 基于 SETNX 实现
- 设置过期时间防止死锁
- Redlock 算法
- 锁续期问题：Redisson 看门狗机制

### 限流
- 固定窗口计数器
- 滑动窗口计数器
- 令牌桶算法
- 漏桶算法
