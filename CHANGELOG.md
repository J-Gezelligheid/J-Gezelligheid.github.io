# CHANGELOG

## 2026-10-13

### Added

- 从原本地仓库复制完整 Git 历史，建立 `personal_homepage` 独立工作仓库。
- 补齐 `AGENTS.md`、`STATE.md`、`TASKS.md`、`CHANGELOG.md`。
- 新增栏目维护指南、Gmail / TopSight 接入计划与离线检查报告。
- 新增标准库 `scripts/validate_site.py`、抓取依赖清单和 `.gitignore`。

### Changed

- README 增加维护入口；原 README 完整保留在 `docs/original_readme.md`。
- `_config.yml` 排除维护文档、脚本与本地配置；页面路径与栏目数据保持复制基线。
- origin 指向原 GitHub 上游，维护使用 `codex/homepage-maintenance` 分支。

### Fixed

- 补齐缺失的维护说明与本地构建 / 私密配置忽略规则。

### Notes

- 原工作区复制前干净；原目录保持不变。
- 当前会话未提供 CORDIS MCP 工具，未执行 CORDIS 生命周期调用。
- 离线检查 0 项错误；数据陈旧和摘要缺失作为告警记录，未伪造修补。
- 未执行联网内容更新、未测试 TopSight 密钥、未推送或发布。

### Next

- 完成 Gmail 账户连接，获得 TopSight 官方接口说明后继续数据源接入。
- 安装并验证独立依赖环境，完善失败保护，完成 Jekyll 构建与视觉预览。
