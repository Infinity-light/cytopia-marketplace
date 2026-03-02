# Changelog

## [2.1.0] - 2026-03-03

### Added
- 迁移到 Claude Code Plugin Marketplace 格式
- 新增 marketplace.json 定义 infinity-workflows marketplace
- 新增 plugin.json 定义 workflow-kit plugin
- 新增 migrate.py 热迁移脚本，支持用户无缝迁移
- 新增 validate.py 契约验证脚本

### Changed
- 所有 skills 从 ~/.claude/skills/ 迁移到 plugin 内部结构
- 支持版本化安装和自动更新
- CLAUDE.md 作为 plugin 提示词加载

### Included Skills
- deploy
- diagnosis
- discovery
- documentation-update
- execution
- key-reader
- learned
- planning
- skills-updater
- verification
- smart-fetch
- ui-ux-pro-max
- frontend-design
- vue-best-practices

### Migration Guide
1. 更新仓库：`git pull origin main`
2. 运行迁移：`python src/migrate.py`
3. 重启 Claude Code
4. 验证安装：`/plugin list`
