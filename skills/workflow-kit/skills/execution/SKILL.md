---
name: execution
description: 当用户有明确计划、需要实际动手完成任务时使用。通过子代理执行契约生成、验证资产生成与 TDD 实现闭环。
---
<!-- ---
role: Execution阶段Skill，通过Subagent按文件契约逐个实现代码，执行TDD流程
depends:
  - references/workflows/coding.md
  - references/workflows/general.md
  - references/workflows/content-writing.md
  - references/practices/python-patterns.md
  - references/practices/testing-standards.md
  - references/practices/backend-patterns.md
  - references/practices/coding-standards.md
  - references/practices/security-checklist.md
  - references/practices/typescript-patterns.md
  - references/practices/react-patterns.md
status: PENDING
--- -->

## 铁律

没有通过规格审查的任务不算完成。主 Agent 只调度，不直接执行。

**【绝对铁律 - 子代理强制执行】**
**所有代码撰写、文件修改、文件创建操作，必须通过 Task 工具调用 Subagent 完成。没有任何例外。**

主 Agent 禁止直接使用 Edit / Write / NotebookEdit 工具。
主 Agent 只能使用 Read / Glob / Grep / Task / AskUserQuestion / TaskCreate / TaskUpdate / TaskList / TaskGet / Skill 工具。

---

## 阶段重构说明

验证与测试门禁已从 Planning 移动到 Execution。
Execution 在传统 TDD 前新增两个准备阶段：
1. 先读 PRD + 项目规划 + CLAUDE.md
2. 先生成契约与验证资产，再进入 RED/GREEN/审查循环

---

## 核心流程（新版）

```
阶段A: 读取 PRD + 项目规划 + CLAUDE.md
  ↓
阶段B: 子代理一次性生成全量契约文件（优先把契约写在主文件头部）
  ↓
阶段C: 子代理生成验证资产（测试骨架 + validate）并做预验证
  ↓
阶段D: 进入既有 TDD RED / GREEN / 规格审查循环
  ↓
阶段E: 更新进度并收敛收尾
```

### 阶段A：上下文装载（先于 TDD）

执行要点：
- 读取 Discovery PRD：`.claude/discovery/[项目名]-[YYYYMMDD-HHmm]-PRD.md`
- 读取 Planning 产物：`.claude/planning/[项目名]-[YYYYMMDD-HHmm]-项目规划.md`
- 读取项目 `CLAUDE.md`

目标：统一需求边界、技术决策依据、实施约束，避免“只看局部文件就开工”。

### 阶段B：契约一次性生成（先于 TDD）

启动**第一个子代理**，一次性完成全量契约文件生成：
- 按项目规划拆分代码文件
- 优先将契约嵌入主代码文件头部（而非散落外部文档）
- 契约至少包含：role / depends / exports / status / functions
- status 初始值为 `PENDING`

目标：先形成可扫描、可追踪、可审查的契约基线。

### 阶段C：验证资产生成与预验证（先于 TDD）

再启动子代理完成：
1. 生成测试骨架（单元 + 集成）
2. 生成 `.claude/validate.py`
3. 运行预验证（例如 validate 与测试收集）

要求：
- 测试骨架可追溯到契约和验收标准
- 预验证失败要先修复，再进入 TDD

---

## 契约驱动开发（TDD 主循环）

### 1. 运行进度扫描

```bash
python -X utf8 .claude/scripts/scan_contracts.py <项目根目录>
```

读取 `.claude/progress.md`，识别：
- PENDING 且依赖满足的文件（可执行）
- IMPLEMENTED 待审查文件

### 2. 确定下一个实现单元

从“下一步可执行”中按依赖顺序选择目标文件。

### 3. TDD RED 阶段（子代理）

- 在测试文件中把 TODO 变为具体断言
- 依据契约行为描述编写断言
- 运行测试并确认先失败（RED）

### 4. TDD GREEN 阶段（子代理）

- 按契约实现目标文件
- 不改契约主体（除 status 外）
- 运行测试并通过（GREEN）
- 通过后将 status 更新为 `IMPLEMENTED`

### 5. 规格审查（独立子代理）

逐条核对契约与实现一致性：
- functions 是否完整实现
- 行为、边界、错误处理是否符合契约
- 依赖关系是否正确
- 测试是否通过

通过后将 status 更新为 `VERIFIED`；不通过则列问题并回到修复。

### 6. 更新进度并迭代

- 重新运行扫描脚本更新 `.claude/progress.md`
- 回到“确定下一个实现单元”继续循环

### 7. 涌现处理

如果发现契约不合理：
- 子代理先暂停并报告
- 主 Agent 评估影响范围
  - 小范围：调度子代理修正契约并继续
  - 大范围：用 AskUserQuestion 与用户确认，必要时回到 Planning

### 8. 全部完成

所有文件 `VERIFIED` 后：
- 最终扫描确认完成度
- 向用户汇报结果

---

## 阶段结束

所有任务完成后，用 AskUserQuestion 向用户确认下一步，选项必须包含：
- "进入 Deploy"（推荐）
- "需要补充任务"
- "暂停"
