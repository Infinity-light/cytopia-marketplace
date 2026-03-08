---
name: plugin-publisher
description: Publish and verify Claude plugins end to end, especially workflow-kit style plugins. Use when you need to identify the canonical source, sync plugin.json and marketplace.json versions, publish to cloud, update/install locally, and prove both installation state and current-session adoption.
---
<!-- ---
role: Claude Plugin 全链路发布与生效验证辅助 Skill，覆盖 canonical source 判定、版本/索引同步、云端发布、本地更新安装与三层验证
depends:
  - references/publishing-topology.md
  - references/verification-rules.md
  - scripts/check_local_plugin_state.py
status: PENDING
--- -->

# Plugin Publisher

面向 Claude Plugin 体系的发布与生效验证 Skill。

它不是独立 plugin，而是 workflow-kit 内部的发布操作 Skill，用于帮助发布类似 `workflow-kit` 这样的 Claude plugin，并严格区分：

1. **安装态已更新**：本地索引、安装记录、缓存目录已经指向新版本。
2. **当前会话已确认使用新版**：当前 Claude 会话已经能确认读取到新版内容，而不是仍停留在旧缓存/旧上下文。

## 何时使用

当用户要做以下事情时加载本 Skill：

- 发布新的 Claude plugin 版本
- 发布 marketplace 中已有 plugin 的更新
- 检查 `plugin.json` / `marketplace.json` / 本地安装态是否一致
- 验证某次发布是否真的对当前会话生效
- 排查“已经 install 了，但 Claude 仍像在用旧版”的问题
- 发布 `workflow-kit` 自身并验证新 Skill / 新内容是否可被加载

## 核心原则

### 1. Canonical source 必须先判定

发布前先明确 **唯一 canonical source**，否则不允许继续：

- 对 plugin 元数据，默认以仓库中的 `skills/<plugin>/plugin.json` 为 plugin canonical source
- 对 marketplace 索引，默认以仓库中的 `.claude-plugin/marketplace.json` 为 marketplace canonical source
- 对已安装状态，默认以本机 `~/.claude/plugins/installed_plugins.json` 为 installed-state source of truth
- 对本地缓存内容，默认以 `~/.claude/plugins/cache/<marketplace>/<plugin>/<version>/` 为 install payload evidence

如果用户提供了多个副本、多个分支、多个工作区，先确认哪一个是发布源。未确认前不做发布动作。

### 2. 发布先同步，再外发

发布顺序必须满足：

1. 确认 canonical source
2. 检查 `plugin.json.version`
3. 检查 `.claude-plugin/marketplace.json` 中对应 plugin 条目版本
4. 检查名称、source、description、keywords 是否需要同步
5. 只有本地版本与索引一致后，才进入云端发布

### 3. 高风险外部动作必须先征得用户确认

以下动作必须在执行前明确向用户确认：

- 推送远程仓库
- 创建 release / tag
- 调用 `claude plugin marketplace update ...`
- 调用 `claude plugin install ...`
- 卸载、重装、覆盖本地缓存
- 删除缓存目录或 installed state 相关文件

默认策略：
- **读操作可直接做**
- **会改变远端、会改变本地安装态、会影响用户环境的操作，必须确认**

## 发布工作流

### 阶段 A：识别发布对象

至少确认以下信息：

- plugin 名称
- marketplace 名称
- canonical source 所在仓库路径
- 目标版本
- 是否只是本地验证，还是要实际云端发布

对 `workflow-kit`，通常对应：

- plugin: `workflow-kit`
- plugin manifest: `skills/workflow-kit/plugin.json`
- marketplace index: `.claude-plugin/marketplace.json`

### 阶段 B：本地发布前检查

读取并比对：

- `plugin.json`
- `.claude-plugin/marketplace.json`
- 如有需要，再检查 README 中声明的版本文本

必须确认：

- plugin 名称一致
- marketplace 中该 plugin 的 `name/source/version` 与 plugin 实体一致
- 版本号已经提升到目标版本
- 新增 skill/内容已经进入 plugin source tree

### 阶段 C：本地状态检查

运行：

```bash
python -X utf8 scripts/check_local_plugin_state.py --plugin <plugin> --marketplace <marketplace>
```

重点检查：

- `installed_plugins.json`
- `known_marketplaces.json`
- cache installPath
- version / gitCommitSha
- 目标文件或内容锚点是否存在于缓存安装目录

如果正在发布 `workflow-kit`，建议额外检查新 skill 的锚点，例如：

- `skills/plugin-publisher/SKILL.md`
- 新增 reference 文件名
- 新增脚本文件名
- 某个专门的唯一文本锚点

### 阶段 D：云端发布

仅在用户确认后执行。

常见动作可能包括：

1. 提交版本同步改动
2. 推送 canonical source 到远端
3. 创建 tag / release
4. 确保 marketplace 可从远端读取到新版本索引

如果任一外部步骤失败，先停止，不要继续做本地安装验证冒充“已发布成功”。

### 阶段 E：本地 marketplace update / install

仅在用户确认后执行：

```bash
claude plugin marketplace update <marketplace>
claude plugin install <plugin>@<marketplace>
```

必要时可补充：

```bash
claude plugin list --json
```

若用户要求强制重装，应再次确认其接受潜在覆盖行为。

## 三层验证模型

发布完成后必须按三层验证，不可只看其中一层。

### 第一层：installed state

检查 `installed_plugins.json`：

- plugin key 是否存在
- version 是否为目标版本
- installPath 是否指向目标版本目录
- 如有 `gitCommitSha`，是否与目标发布一致

### 第二层：cache payload

检查缓存安装目录：

- 目标版本目录是否存在
- `plugin.json` / `SKILL.md` / scripts / references 是否存在
- 内容锚点是否存在

### 第三层：content anchor

验证某个**只有新版本才会出现**的内容锚点，例如：

- 新 skill 目录名
- 新文档标题
- 新脚本中的唯一函数名/说明文本

只有三层都通过，才能说：

- “本地安装态已更新”

## 会话生效验证

这一步与“三层验证”不同。

即使安装态已更新，也不能自动得出“当前会话已经在使用新版”。

需要额外区分两种结论：

### 结论 1：安装态已更新

满足条件：

- `installed_plugins.json` 正确
- cache 正确
- 内容锚点正确

但这只能证明磁盘上的安装结果正确。

### 结论 2：当前会话已确认使用新版

必须再做至少一种会话级验证：

- 新开一个 Claude 会话并重新加载目标 skill
- 在当前会话明确触发新 skill，并观察其读取到的新锚点/新行为
- 通过当前会话的实际响应证明新版本内容已被采纳

如果做不到，会话级结论必须写成：

- “已确认安装更新，但尚未确认当前会话已切换到新版上下文”

不得混写成“发布完成且已生效”。

## 失败分支

### A. `plugin.json` 与 marketplace 版本不一致

停止发布，先同步版本与索引。

### B. marketplace update 后仍读到旧版本

检查：

- 远端默认分支是否已包含新索引
- marketplace source 是否指向错误仓库/分支
- CDN / 拉取缓存是否尚未刷新

### C. install 后 installed state 已更新，但缓存内容没有新文件

怀疑：

- 安装路径错误
- marketplace 条目 source 指向错误目录
- 目标版本包内容未正确构建/提交

### D. 缓存内容已更新，但当前会话表现仍旧

结论应为：

- “安装态已更新，但当前会话尚未确认使用新版”

建议用户：

- 开新会话
- 重新触发 skill
- 再次检查锚点

## 推荐输出格式

### 发布前审查

- Canonical source:
- Target plugin:
- Target marketplace:
- Local plugin version:
- Local marketplace version:
- Sync status:
- External actions requiring confirmation:

### 发布后报告

- Cloud publish:
- Marketplace update:
- Local install:
- Installed state verification:
- Cache verification:
- Content anchor verification:
- Session adoption verification:
- Final conclusion:

## 资源

按需读取：

- `references/publishing-topology.md`
- `references/verification-rules.md`
- `scripts/check_local_plugin_state.py`
