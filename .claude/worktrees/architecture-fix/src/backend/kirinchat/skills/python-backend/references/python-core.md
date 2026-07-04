# Python 核心知识点

## 数据模型
- 一切皆对象，函数是一等公民
- 特殊方法：__init__/__str__/__repr__/__len__/__getitem__
- 可调用对象：函数、lambda、类、实现了 __call__ 的实例

## 装饰器
- 本质是高阶函数，接受函数返回函数
- functools.wraps 保留原函数元信息
- 带参数的装饰器（三层嵌套）
- 类装饰器

## 生成器与迭代器
- 迭代器协议：__iter__ + __next__
- yield 关键字、生成器表达式
- send() 方法实现协程通信
- itertools 模块

## GIL（全局解释器锁）
- CPython 的实现细节，不是语言特性
- 限制同一时刻只有一个线程执行字节码
- 对 I/O 密集型影响小，对 CPU 密集型影响大
- multiprocessing 绕过 GIL

## 内存管理
- 引用计数为主，分代回收为辅
- weakref 弱引用
- __slots__ 减少内存占用
- gc 模块手动控制

## 元编程
- 元类 type/metaclass
- 描述符协议：__get__/__set__/__delete__
- __new__ vs __init__
