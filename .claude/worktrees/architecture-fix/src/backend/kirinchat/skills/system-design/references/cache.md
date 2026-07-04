# 缓存设计知识点

## 缓存策略
- Cache Aside：先更新 DB，再删缓存
- Read/Write Through：缓存层统一读写
- Write Behind：异步写回 DB

## 缓存问题
- 缓存穿透：查询不存在的数据，用布隆过滤器/空值缓存
- 缓存击穿：热点 key 过期，用互斥锁/永不过期
- 缓存雪崩：大量 key 同时过期，用随机过期时间

## Redis 数据结构
- String：计数器、分布式锁
- Hash：对象存储
- List：消息队列
- Set：去重、交并差集
- ZSet：排行榜、延迟队列

## Redis 高可用
- 主从复制：读写分离
- Sentinel：自动故障转移
- Cluster：数据分片（16384 槽）

## 缓存一致性
- 延迟双删
- 订阅 Binlog（Canal）
- 设置合理过期时间作为兜底
