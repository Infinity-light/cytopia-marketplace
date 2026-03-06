---
name: planning
description: 当用户已明确方向、需要做关键决策与落地规划时使用。基于 Discovery 的 PRD 形成可执行项目规划，不在本阶段写代码或生成工程骨架。
---
<!-- ---
role: Planning阶段Skill，基于PRD完成决策与项目规划
depends:
  - references/module-template.md
  - references/architecture-checklist.md
  - references/frontend-design-checklist.md
  - references/module-checklist.md
status: PENDING
--- -->

## 阶段定位（强制）

Planning 只做**决策与规划**，不做实现落地。

本阶段**不执行**以下事项：
- 不写项目骨架文件
- 不写文件契约
- 不写测试骨架
- 不写 `.claude/validate.py`
- 不运行 `pytest` 或测试门禁

> 说明：验证与测试门禁已移动到 Execution 阶段。

---

## 输入读取规则

### 1) 读取 Discovery 的 PRD（时间戳版）

优先级如下：
1. 使用 Discovery 交接时明确给出的 PRD 路径
2. 若未给路径，则在 `.claude/discovery/` 下查找最新匹配文件：
   - 命名格式：`[项目名]-[YYYYMMDD-HHmm]-PRD.md`

### 2) 读取项目上下文

- 读取项目 `CLAUDE.md`（如存在）
- 识别已有技术栈、架构约束、组织规范

---

## 核心流程

```
步骤1: 读取并理解 PRD 与项目上下文
  ↓
步骤2: 提炼必须决策项（技术栈/架构/边界）
  ↓
步骤3: 用 AskUserQuestion 驱动关键决策（给出对比与取舍）
  ↓
步骤4: 汇总为项目规划文档（强调 why）
  ↓
步骤5: 用户确认后进入 Execution
```

### 步骤1：理解问题与约束

- 明确业务目标、范围边界、验收口径
- 明确非功能要求：性能、安全、可维护性、成本、交付周期
- 明确与现有系统的兼容约束

### 步骤2：提炼关键决策清单

至少覆盖：
- 技术栈决策（语言/框架/数据库/部署形态）
- 核心架构决策（单体/模块化/服务化、同步/异步）
- 数据与接口策略（一致性、幂等、版本化）
- 质量保障策略（在 Execution 如何验收）

### 步骤3：AskUserQuestion 驱动决策（强制）

对每个关键决策，必须用 AskUserQuestion 给出**可比较选项**，并在提问上下文包含：
- 每个选项的优点
- 每个选项的风险/成本
- 适用场景
- 推荐项及推荐理由

要求：
- 不给“空泛选项”
- 不让用户在缺乏对比信息下拍板
- 关键决策必须留痕到规划文档

### 步骤4：形成项目规划文档

#### 命名规范（强制）

规划文档必须使用：

```
[项目名]-[YYYYMMDD-HHmm]-项目规划.md
```

**存储位置（强制）**：`.claude/planning/[项目名]-[YYYYMMDD-HHmm]-项目规划.md`

#### 输出结构（强调 why）

推荐结构：

```markdown
# 项目规划：[项目名]

## 1. 背景与目标
- 要解决的问题
- 目标与成功标准

## 2. 关键决策与依据（Why）
### 2.1 决策项 A
- 候选方案对比（优缺点/成本/风险）
- 最终选择
- 选择理由（为什么）
- 不选其他方案的原因

### 2.2 决策项 B
...

## 3. 实施范围与阶段划分
- 本期范围
- 非本期范围
- 里程碑建议

## 4. 执行策略（给 Execution）
- 推荐实施顺序
- 关键依赖与风险前置
- 验证与测试门禁在 Execution 的落点

## 5. 风险与应对
- 技术风险
- 交付风险
- 回滚与兜底策略
```

**写作要求**：
- 先讲“为什么”，再讲“做什么”
- 每个重要结论必须能追溯到 PRD 或用户决策
- 避免仅列清单、不解释取舍

---

## 阶段结束

用 AskUserQuestion 向用户确认下一步，选项必须包含：
- **进入 Execution（推荐）**
- **需要修改项目规划**
- **暂停**

并明确输出交接路径：

```
PRD 文件路径：.claude/discovery/[项目名]-[YYYYMMDD-HHmm]-PRD.md
项目规划路径：.claude/planning/[项目名]-[YYYYMMDD-HHmm]-项目规划.md
```
