# TypeScript 核心知识点

## 基础类型
- 原始类型：string/number/boolean/null/undefined/symbol/bigint
- 特殊类型：any/unknown/never/void
- 联合类型、交叉类型、字面量类型

## 类型体操
- Partial/Required/Readonly/Pick/Omit
- Record/Mapped Types
- Conditional Types：`T extends U ? X : Y`
- infer 关键字
- Template Literal Types

## 泛型
- 泛型函数、泛型接口、泛型类
- 泛型约束 `extends`
- 泛型默认值

## 类型守卫
- typeof/instanceof/in
- 自定义类型守卫 `is`
- const assertions、satisfies

## 模块系统
- ES Modules vs CommonJS
- 声明文件 (.d.ts)
- 模块解析策略
