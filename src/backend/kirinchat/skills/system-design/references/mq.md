# 消息队列知识点

## 为什么需要 MQ
- 异步处理：提升响应速度
- 流量削峰：缓冲突发流量
- 系统解耦：服务间解依赖

## 常见 MQ 对比
- RabbitMQ：AMQP 协议，功能丰富，适合中小规模
- Kafka：高吞吐，适合日志/大数据流
- RocketMQ：阿里开源，事务消息，适合电商
- Redis Stream：轻量级，适合简单场景

## 核心概念
- Producer/Consumer/Broker
- Topic/Queue/Partition
- Consumer Group：负载均衡消费
- Offset：消费位移管理

## 可靠性保证
- 消息确认：ACK 机制
- 持久化：消息落盘
- 重试机制：消费失败自动重试
- 死信队列：多次重试失败的消息
- 幂等消费：去重表/唯一 ID

## 延迟消息
- RabbitMQ：TTL + 死信队列
- RocketMQ：原生延迟级别
- Redis：ZSet + 时间戳轮询
