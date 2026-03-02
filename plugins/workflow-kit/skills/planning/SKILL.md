---
name: planning
description: 当用户知道要做什么但不知道怎么做时使用。将 Discovery 的 PRD 转化为可直接实现的工程化文件骨架。主 Agent 内部完成文件契约编写。
---

## 铁律

1. **没有文件骨架不进入 Execution**
2. **validate.py 不通过不进入 Execution**
3. **集成测试骨架不运行不进入 Execution**

## 核心原则

- **主 Agent 直接写文件契约** — 不再调度子代理写契约，保证架构一致性
- **契约写在文件里** — 信息和实现共生，减少跨边界衰减
- **测试骨架只写描述和 TODO** — 断言是 Execution RED 阶段的事
- **不做约束探测** — SSH/DNS/环境检查移到 Deploy 阶段
- **静态架构 ≠ 运行时集成** — 文件契约描述编译时结构，`validate.py` 和集成测试验证运行时连接性。两者缺一不可

## 核心流程

```
步骤1: 读取 PRD + 技术选型（主Agent）
  ↓
步骤2: 架构设计（主Agent 内部完成）
  ↓
步骤3: 创建文件契约（主Agent 直接写）
  ↓
步骤4: 创建测试骨架（主Agent 直接写）
  ↓
步骤5: 用户确认 → 更新 CLAUDE.md → 进入 Execution
```

---

### 步骤1: 读取 PRD

**执行者**：主 Agent 自己完成。

1. **读取 Discovery 产出**：从 `.claude/discovery/PRD.md` 读取需求文档
2. **读取探索性制品**：从 `.claude/exploration/` 读取用户选中的原型
3. **读取项目 CLAUDE.md**：了解已有的技术栈和架构（如果是已有项目）
4. **技术选型确认**：PRD 中用户已选定方案，此处仅确认，不再重复调研

---

### 步骤2: 架构设计

**执行者**：主 Agent 内部完成。

基于 PRD 设计：
- **目录结构**（精确到每个文件）
- **模块划分**和模块间依赖关系
- **数据流向**
- **外援依赖清单**（外部 API 或重型本地服务）
- **环境变量清单**
- **前后端通信约定**（如适用）
- **数据库设计**（如适用）

#### 外援依赖清单（重要）

**定义**：外援依赖指需要外部网络服务或本地重型计算资源的依赖，包括：
- **外部 API**：需要网络调用和 API Key 的第三方服务
- **重型本地服务**：运行时自动下载大型模型（>500MB）或需要 GPU 的深度学习框架

**普通 Python 包不算外援依赖**（如 requests, pydantic, click 等）。

**外援依赖清单格式**：

| 依赖名 | 版本 | 类型 | 用途 | 安装/配置要求 | 备注 |
|--------|------|------|------|---------------|------|
| OpenAI API | - | 外部 API | GPT-4 调用 | 需 `OPENAI_API_KEY` | 按 token 计费 |
| Whisper | ≥20231117 | 重型本地 | 语音转文字 | 首次自动下载 ~2GB 模型 | 离线可用 |
| pyannote.audio | ≥3.1.0 | 重型本地 | 说话人分离 | 需 HuggingFace token | 离线可用 |
| PaddleOCR | ≥2.7.0 | 重型本地 | 中文 OCR | 首次自动下载 ~100MB 模型 | 离线可用 |

**注意**：此时不做 SSH/域名/服务器等约束探测，这些在 Deploy 阶段处理。

---

### 步骤3: 创建文件契约（核心步骤）

**执行者**：主 Agent 直接写文件。

根据架构设计，创建项目中所有实际代码文件，每个文件只包含头部契约注释，没有实现代码。

**契约格式（YAML frontmatter）**：

**TypeScript/JavaScript**：
```typescript
/**
 * ---
 * role: [文件职责一句话描述]
 * depends: [依赖文件路径列表]
 * exports: [导出接口/组件名列表]
 * status: PENDING
 * functions:
 *   - functionName(param: type): ReturnType
 *     行为描述，包括边界条件和错误处理
 * ---
 */
```

**Python**：
```python
"""
---
role: [文件职责一句话描述]
depends: [依赖文件路径列表]
exports: [导出函数/类名列表]
status: PENDING
functions:
  - function_name(param: type) -> ReturnType
    行为描述，包括边界条件和错误处理
---
"""
```

**契约完整性检查**：
- [ ] role：一句话描述文件职责
- [ ] depends：依赖的文件路径列表（相对路径）
- [ ] exports：本文件导出的接口/函数/类名
- [ ] functions：每个函数的签名和行为描述
- [ ] status：PENDING（Execution 阶段会更新）

**依赖关系检查**：
- [ ] 检查是否有循环依赖
- [ ] 确认依赖图是 DAG（有向无环图）

---

### 步骤4: 创建测试骨架

**执行者**：主 Agent 直接写文件。

#### 4.1 单元测试骨架
为每个有 `functions` 的文件创建对应的测试文件：

- 只有 `describe/test` 块和描述文字
- 断言部分写 `// TODO: implement assertion`
- 测试用例来源于 PRD 的验收标准和契约中的行为描述

#### 4.2 集成测试骨架（关键补充）
创建 `tests/test_integration/` 目录，包含：

- 测试真实对象的集成能力（**禁止使用 Mock**）
- 验证模块间导入和调用关系
- 验证依赖图是连通的（不是孤立的文件）

**必须包含的测试**：
- `test_imports.py` - 验证所有模块可以正确导入
- `test_component_integration.py` - 验证核心组件可以实例化和交互
- `test_contract_compliance.py` - 验证实现符合文件契约定义

---

### 步骤5: 创建验证脚本

**执行者**：主 Agent 直接写文件。

创建 `.claude/validate.py` - **可执行**的契约验证脚本：

**功能要求**：
1. **导入检查**：验证所有 `depends` 中的依赖可以正确导入
2. **重复定义检查**：扫描所有 Python 文件，检测同名类/函数在多处定义
3. **组件同步检查**：验证 GUI、Orchestrator 等入口点的组件列表与 `src/installers/` 或对应目录一致
4. **契约完整性检查**：验证每个文件的 YAML frontmatter 包含必需字段

**调用方式**：
```bash
python .claude/validate.py              # 完整验证
python .claude/validate.py --check-planning  # Planning 阶段专用：检查骨架完整性
```

**返回码**：0 = 通过，非0 = 失败并输出具体错误

---

### 步骤6: 固化

1. **运行进度扫描脚本**：
   ```bash
   python -X utf8 .claude/scripts/scan_contracts.py <项目根目录>
   ```
   生成 `.claude/progress.md`

2. **用 AskUserQuestion 让用户确认整体骨架**

3. **更新项目 CLAUDE.md**：将本轮新增的架构信息写入
   - 新增的模块和职责
   - 技术选型决策
   - 目录结构

---

## 阶段结束

### 强制检查点：Planning 完成验证

**在询问用户之前，必须执行以下验证**：

```bash
# 1. 运行验证脚本
python .claude/validate.py --check-planning

# 2. 运行集成测试骨架（应该全部通过或合理跳过）
pytest tests/test_integration/ -v
```

**验证失败的处理**：
- 如果 `validate.py` 报告错误（重复定义、导入失败、组件不同步等）→ **必须修复后才能进入 Execution**
- 如果集成测试无法运行 → 检查测试骨架是否正确创建
- 绝不允许带着 "骨架已准备好" 的假象进入 Execution

### 用户确认

验证通过后，用 AskUserQuestion 向用户确认下一步：

选项必须包含：
- "进入 Execution"（推荐，仅当验证通过时显示）
- "需要修改骨架"
- "暂停"

---

## 契约示例

### TypeScript 示例

```typescript
/**
 * ---
 * role: 用户认证模块，处理登录/注册/登出逻辑
 * depends:
 *   - ./types.ts
 *   - ../utils/crypto.ts
 * exports:
 *   - AuthService
 *   - useAuth hook
 * status: PENDING
 * functions:
 *   - login(email: string, password: string): Promise<AuthResult>
 *     验证用户凭据，成功返回 token，失败抛出 AuthError
 *   - register(email: string, password: string, name: string): Promise<User>
 *     创建新用户，检查邮箱是否已存在
 *   - logout(): Promise<void>
 *     清除本地 token，调用后端注销接口
 * ---
 */
```

### Python 示例

```python
"""
---
role: 数据预处理模块，清洗和转换原始数据
depends:
  - ./models.py
  - ../config/settings.py
exports:
  - DataCleaner
  - normalize_text
  - validate_schema
status: PENDING
functions:
  - DataCleaner.clean(df: DataFrame) -> DataFrame
    清洗数据，处理缺失值和异常值，返回清洗后的 DataFrame
  - normalize_text(text: str) -> str
    标准化文本，去除多余空格、统一大小写、处理特殊字符
  - validate_schema(data: dict, schema: dict) -> bool
    验证数据是否符合指定 schema，不符合时抛出 ValidationError
---
"""
```
