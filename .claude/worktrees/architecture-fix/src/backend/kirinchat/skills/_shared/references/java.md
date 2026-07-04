# Java 核心知识点

## 面向对象

### 封装
- 访问修饰符：private、default、protected、public
- Java Bean 规范：getter/setter、无参构造函数、实现 Serializable

### 继承
- 单继承限制与接口多实现
- super 关键字的使用
- 方法重写（Override）规则：返回值类型、访问权限、异常处理
- 构造函数的执行顺序

### 多态
- 编译时多态（方法重载）vs 运行时多态（方法重写）
- 向上转型与向下转型
- instanceof 关键字

### 抽象
- 抽象类 vs 接口的区别与选择
- Java 8 接口新特性：default 方法、static 方法
- 函数式接口与 Lambda 表达式

## 集合框架

### List
- ArrayList vs LinkedList：底层实现、时间复杂度、适用场景
- ArrayList 扩容机制：1.5 倍扩容、Arrays.copyOf
- CopyOnWriteArrayList：写时复制、适用场景

### Map
- HashMap 底层实现：数组 + 链表 + 红黑树
- HashMap 的 hash 函数与扰动函数
- HashMap 扩容机制与 rehash
- ConcurrentHashMap 的实现：JDK 7 分段锁 vs JDK 8 CAS + synchronized
- LinkedHashMap：有序性、LRU 缓存实现

### Set
- HashSet 底层基于 HashMap
- TreeSet 红黑树实现与排序

### 迭代器
- Iterator 与 fail-fast 机制
- Iterable 接口与 for-each 循环

## 多线程

### 线程创建
- 继承 Thread vs 实现 Runnable vs 实现 Callable
- 线程池：ThreadPoolExecutor 核心参数、线程池类型与选择
- 线程的生命周期与状态转换

### 锁
- synchronized：对象锁、类锁、锁升级（偏向锁 -> 轻量级锁 -> 重量级锁）
- ReentrantLock：公平锁与非公平锁、可中断、超时机制
- ReadWriteLock：读写锁分离

### 并发工具
- volatile 关键字：可见性、禁止指令重排
- CAS 操作与 Unsafe 类
- CountDownLatch、CyclicBarrier、Semaphore
- ThreadLocal：原理与内存泄漏
- CompletableFuture：异步编程

## JVM

### 内存模型
- 运行时数据区：堆、栈、方法区、程序计数器、本地方法栈
- 堆内存分代：年轻代（Eden、Survivor）、老年代
- 栈帧结构：局部变量表、操作数栈、动态链接、方法返回地址
- Java 内存模型（JMM）：happens-before 原则

### 垃圾回收
- 可达性分析算法：GC Roots
- 垃圾回收算法：标记-清除、标记-整理、复制算法
- 垃圾收集器：Serial、Parallel、CMS、G1、ZGC
- GC 调优：常用参数、日志分析

### 类加载
- 类加载过程：加载 -> 验证 -> 准备 -> 解析 -> 初始化
- 双亲委派模型
- 打破双亲委派：SPI、OSGi、Tomcat 自定义类加载器
