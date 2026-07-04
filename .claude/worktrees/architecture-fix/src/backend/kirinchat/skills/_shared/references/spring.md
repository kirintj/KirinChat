# Spring 核心知识点

## IoC

### 容器
- BeanFactory vs ApplicationContext
- 容器启动过程：BeanDefinition 加载、注册、实例化
- Bean 的作用域：singleton、prototype、request、session

### 依赖注入
- 构造器注入 vs 字段注入 vs Setter 注入
- @Autowired 按类型注入与 @Qualifier 按名称注入
- @Resource（JSR-250）与 @Inject（JSR-330）

### Bean 生命周期
- 实例化 -> 属性填充 -> Aware 回调 -> BeanPostProcessor 前置处理 -> InitializingBean/init-method -> BeanPostProcessor 后置处理 -> 使用 -> DisposableBean/destroy-method
- 循环依赖的解决：三级缓存（singletonObjects、earlySingletonObjects、singletonFactories）

## AOP

### 概念
- 切面（Aspect）、切点（Pointcut）、通知（Advice）
- 连接点（Join Point）、引入（Introduction）
- 通知类型：@Before、@After、@AfterReturning、@AfterThrowing、@Around

### 实现
- JDK 动态代理：基于接口，Proxy + InvocationHandler
- CGLIB 代理：基于继承，生成子类
- Spring 如何选择代理方式
- AOP 的实际应用：日志记录、权限控制、事务管理、性能监控

## Spring Boot

### 自动配置
- @SpringBootApplication 注解组合：@SpringBootConfiguration + @EnableAutoConfiguration + @ComponentScan
- 自动配置原理：spring.factories / AutoConfiguration.imports -> 条件注解过滤
- 条件注解：@ConditionalOnClass、@ConditionalOnProperty、@ConditionalOnBean

### Starter
- 自定义 Starter 的开发流程
- 命名规范：spring-boot-starter-xxx / xxx-spring-boot-starter
- 配置属性类：@ConfigurationProperties
- META-INF/spring.factories 或 META-INF/spring/org.springframework.boot.autoconfigure.AutoConfiguration.imports

## Spring Cloud

### 服务发现
- Eureka：AP 模型、自我保护机制
- Nacos：CP/AP 切换、配置管理
- 注册中心的作用与选型

### 配置中心
- Spring Cloud Config：Git 存储、动态刷新
- Nacos Config：长轮询、灰度发布
- 配置的优先级与覆盖规则

### 网关
- Spring Cloud Gateway：路由、过滤器、限流
- Gateway vs Zuul 对比
- 请求路由匹配规则
- 全局过滤器与自定义过滤器

### 熔断降级
- Sentinel：流控规则、降级规则、热点参数限流
- Resilience4j：熔断器、限流器、重试
- 熔断状态机：关闭 -> 打开 -> 半开
- 服务降级的策略与实现
