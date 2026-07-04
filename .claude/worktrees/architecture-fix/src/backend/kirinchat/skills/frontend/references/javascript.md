# JavaScript 核心知识点

## 原型与原型链
- 每个对象都有 `__proto__` 指向构造函数的 `prototype`
- 原型链的终点是 `null`
- `instanceof` 沿原型链检查

## 作用域与闭包
- 词法作用域在定义时确定
- 闭包 = 函数 + 外部变量引用
- 常见用途：数据封装、函数工厂、模块模式

## 事件循环
- 宏任务：setTimeout/setInterval/I/O
- 微任务：Promise.then/MutationObserver
- 执行顺序：同步代码 → 微任务 → 宏任务

## this 绑定
- 默认绑定：全局对象（严格模式下 undefined）
- 隐式绑定：调用对象
- 显式绑定：call/apply/bind
- new 绑定：新创建的对象
- 箭头函数：继承外层 this

## Promise
- 三种状态：pending/fulfilled/rejected
- 链式调用、错误捕获
- Promise.all/race/allSettled/any 区别

## ES6+ 特性
- 解构赋值、展开运算符、剩余参数
- Map/Set/WeakMap/WeakSet
- Proxy/Reflect
- Symbol/Iterator/Generator
- Optional chaining (?.)、Nullish coalescing (??)
