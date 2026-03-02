# Claude 工作指南

## 第零原则：Skill-First

**Skill 是唯一的工作单元。整个工作流不是"流程里偶尔调用 Skill"，而是"一切工作都是 Skill 的编排"。**

### 四层 Skill-First 法则

**第一层：优先使用现有 Skill**
做任何事之前，先问一个问题：**有没有对应的 Skill？**
- 有 → 立即加载，按 Skill 指导执行
- 没有 → 进入第二层

这条规则不分阶段、不分大小、不分场景：
- 网页抓取失败 → 加载 smart-fetch，不是换 URL 重试
- 写前端组件 → 加载 ui-ux-pro-max，不是直接写代码
- 需要密钥 → 加载 key-reader，不是翻 .env
- 导出文档 → 加载 docx，不是手动拼文件
- 阶段转换 → 加载对应阶段 Skill（discovery / planning / execution...）

**第二层：扩展 Skill 库**
当发现没有可用 Skill 时：
1. 暂停当前任务
2. 加载 `/skills-updater`
3. 创建新 Skill（或从其他项目迁移）
4. 新 Skill 创建完成后，返回第一层使用它

**第三层：执行工作时**
一旦确定使用某个 Skill：
- **严格遵循** Skill 的指导
- **不要跳过** Skill 中定义的步骤
- **不要添加** Skill 外的额外步骤
- 如果遇到问题，**回到 Skill** 查看是否有解决方案

**第四层：任务完成后**
- 记录经验到 `/learned`
- 如果发现了 Skill 的不足，更新对应 Skill
- 如果发现了全新的工作模式，创建新 Skill

---

## 工作流概览

完整的 Claude Code 工作流套件：

```
 discovery → planning → execution → diagnosis → verification
     ↑                                            ↓
     └──────────── documentation-update ←─────────┘
                         ↓
                      deploy
```

### 阶段说明

| Skill | 用途 | 触发时机 |
|-------|------|----------|
| `/discovery` | 需求调研、信息收集 | 任务开始时 |
| `/planning` | 架构设计、方案规划 | 需求明确后 |
| `/execution` | 代码实现 | 方案确定后 |
| `/diagnosis` | 问题诊断、故障排查 | 遇到问题时 |
| `/verification` | 部署验证、质量检查 | 实现完成后 |
| `/documentation-update` | 文档更新 | 任务完成后 |
| `/deploy` | 部署同步 | 验证通过后 |

---

## 辅助 Skills

| Skill | 用途 |
|-------|------|
| `/key-reader` | 读取密钥、配置文件 |
| `/smart-fetch` | 智能网页抓取 |
| `/ui-ux-pro-max` | UI/UX 设计规范 |
| `/frontend-design` | 前端组件设计 |
| `/vue-best-practices` | Vue.js 最佳实践 |
| `/skills-updater` | 更新/创建 Skill |
| `/learned` | 记录学习经验 |

---

## 使用规范

1. **始终先加载 Skill**，再开始工作
2. **不要在 Skill 外自行发挥**
3. **遇到问题先回查 Skill**
4. **完成工作后更新 Skill**（如有不足）

---

## 版本信息

- **Plugin**: workflow-kit
- **Version**: 2.1.0
- **Author**: Infinity-light
- **Repository**: https://github.com/Infinity-light/Cytopia-claude-code-workkit-plugin
