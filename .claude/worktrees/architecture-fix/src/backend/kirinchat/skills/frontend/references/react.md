# React 核心知识点

## 核心概念
- JSX 本质是 React.createElement 的语法糖
- 组件：函数组件 vs 类组件（函数组件为主流）
- Props 不可变、State 可变

## Hooks
- useState：状态管理
- useEffect：副作用处理（依赖数组、清理函数）
- useRef：DOM 引用 / 持久化值
- useMemo/useCallback：性能优化
- useReducer：复杂状态逻辑
- 自定义 Hooks：逻辑复用

## 渲染机制
- Virtual DOM Diff 算法（同层比较、key 的作用）
- Reconciliation 协调过程
- 批量更新（Automatic Batching）
- Suspense 与 Lazy Loading

## 状态管理
- Context API：轻量级全局状态
- Redux Toolkit：中大型应用
- Zustand/Jotai：原子化状态
- React Query/SWR：服务端状态

## 性能优化
- React.memo / useMemo / useCallback
- 代码分割 React.lazy + Suspense
- 虚拟列表（react-window / react-virtuoso）
- 避免内联函数和对象创建

## React 18+ 新特性
- Concurrent Mode
- useTransition / useDeferredValue
- Suspense for Data Fetching
- Server Components（Next.js）
