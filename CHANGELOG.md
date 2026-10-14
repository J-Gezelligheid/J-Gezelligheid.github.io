# CHANGELOG

## 2026-10-14 — Frontier 内容与月度更新

### Added

- TopSight 摘要层面选读 20 篇工作论文，覆盖 9 个经济学主题；公开作者、年份、来源编号及可用 DOI。
- 新转换器、检索计划、选文清单、8 项数据保护测试；原始响应和变更前快照留在忽略目录 `.local`。
- 当前聊天月度 heartbeat `frontier`：每月 1 日 09:00 Asia/Shanghai，用户已授权自动发布至原 GitHub 主页。

### Changed

- Frontier 新增主题筛选、题名/作者/全文摘要文本搜索、摘要折叠与来源说明；保留页面 URL 与原有本地留言。
- 五大期刊和 NBER 旧内容明确标记历史快照；非研究目录项保留数据但不显示为研究论文。
- 修正 Jekyll 时区为 `Asia/Shanghai`。

### Fixed

- 来源失败不清空旧栏目，日期不冒充新收录；中文导读与历史机器译文分别标注。
- 外部文本转义，危险链接过滤；浏览器禁止存储时搜索仍可用，留言保存失败明确提示。

### Notes

- 数据校验 0 错误；8 项安全测试及 Liquid 渲染、筛选/搜索/空状态测试通过。
- 五刊定向检索未取得可收录新记录，部分外部通道超时；保留原日期并公开通道状态。
- CORDIS 工具未在会话暴露，以本地证据与本记录留痕；密钥与原始返回未纳入提交。

### Next

- 核对 GitHub Pages 实际构建与线上页面；继续处理五刊来源可用性，后续接入 Drug Watch。

## 2026-10-14

### Added

- TopSight 0.3.4 本地 MCP 客户端已安装于用户目录，依赖使用独立虚拟环境；未纳入网站仓库。
- 三工具实测通过：额度查询、一次最小三库检索、一条论文读取。

### Changed

- 备份后追加 Codex MCP 配置，已有配置逐项核对保持不变；更新栏目接入状态。

### Fixed

- 为原客户端的 POSIX 权限检查添加严格 Windows ACL 校验，保留原版文件；正反权限检查通过。

### Notes

- 密钥已移到用户专属目录，配置只保存路径；没有打印密钥或将其写入网站仓库。
- 上次配置合并因自动审批服务用量限制未执行，本次经正常审批重试成功。
- 网站页面和数据未改变；未推送或发布。

### Next

- 完全退出并重开 Codex，新建任务仅查询 TopSight 额度；随后继续 Gmail / Frontier 内容转换。

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
