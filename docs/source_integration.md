# 下一阶段数据源接入

2026-10-13 研究者指定：Drug Watch 通过 Gmail 更新，Frontier 依托 TopSight 更新。2026-10-14 已完成 TopSight MCP 安装与配置；Frontier 已完成 TopSight 主题选文转换，Drug Watch 待接入。

## Gmail → Drug Watch

- 研究者已确认 Gmail 安装完成，Gmail 工具已在会话中出现；尚未读取邮件。
- 连接后先识别药物、临床试验、监管和产业资讯订阅邮件，并确定专用 label / 发送者名单与时间窗口。
- 邮件先进入不发布的候选整理流程，提取新闻的原始公开链接、来源、发布日期和简短摘要，再映射到现有三个类别。
- 收件人信息、个人往来、邮箱内部链接、退订链接、带身份 token 的跟踪链接和原始邮件正文不应写入公开 `_data/`。
- 本地候选和中间记录使用 `.local/`，该目录同时被 Git 忽略和 Jekyll 排除。
- Gmail 插件供当前会话读取邮件，不等同于可在 GitHub Actions 使用的 OAuth 授权；未来若要后台定时更新，需要单独设计只读授权与运行环境。
- 当前未读取邮件、未生成邮件候选内容、未启用后台任务。

## TopSight → Frontier

- 官方网站：[TopSight](https://topsight.net/)。官网公开说明文献 API 支持文献检索、摘要与额度查询。
- 官网接入按钮指向 `/api/evidence-lab/literature-api/`；本轮匿名访问于 2026-10-13 返回 HTTP 401。
- 通过用户提供的 `topsight-literature-client-kit-0.3.4.zip` 核对并实测：Base URL 为 `https://topsight.net/api/literature`，客户端使用 Bearer 鉴权。
- 接口：`GET /v1/usage`、`POST /v1/evidence/search`、`GET /v1/evidence/papers/{paper_key}`。
- 安装目录：`C:/Users/Jinca/.codex/mcp/topsight-literature/0.3.4`；独立 Python 在 `.venv/Scripts/python.exe`，客户端位于 `client/`。
- 密钥文件已移到 `C:/Users/Jinca/.codex/secrets/topsight/topsight_api_key.txt`，设置仅当前用户可读写的受保护 ACL；原位置不再保留文件。
- Codex 配置通过 `TOPSIGHT_API_KEY_FILE` 引用私密文件路径，`TOPSIGHT_API_BASE_URL` 指定上述地址；没有在配置、日志或网站仓库中保存密钥值。
- 原包权限检查按 POSIX 设计，Windows 适配使用 pywin32 验证所有者、受保护 DACL、单一当前用户访问规则并拒绝重解析点；原版文件保存在安装目录的 `upstream/`。
- 验收报告为安装目录的 `verification.json`（仅通过标志），配置合并报告为 `config_merge_report.json`，依赖版本记录为 `requirements-resolved.txt`；配置原文备份位于私密目录的 `config_backups/`。
- 已验证三个工具发现与实际调用：一次额度查询、以 inflation 为测试词的一次三库检索（每库最多 1 条）、一条返回论文的读取，全部通过。论文正文响应未保存到日志或仓库。
- 检索字段包括 `terms`（1–3 个核心概念）、`corpora`、`mode`、年份、期刊、排序与每库数量。返回 `lanes` 区分 `formal`、`external_authority`、`working`；结果是元数据与摘要，不是全文验证或 AI 筛选。
- 当前会话不能代表新配置已在 Codex 内加载：必须完全退出并重开后新建任务，第一句仅查询额度。
- 后续再根据实际字段编写网站转换器和离线契约测试，尤其核对来源日期、中文导读、翻译、卷期及 NBER 来源归属。
- 目标映射到现有 `journals[].papers[]` 与 `nber.papers[]`；非 NBER 工作论文不得放进 NBER 分类，应单独扩展数据和页面。
- TopSight 中文导读与完整摘要翻译须明确区分，不能无条件把导读写进 `abstract_zh`。
- 仅在来源确实给出卷期时保留“最新一期”的表述；按日期检索到的记录应显示为“最新收录 / 最新发表”等与实际口径一致的标题。
- 当前仅完成安装验收，未批量下载论文或改写网站数据。

## 接入验收

1. 两个来源分别完成最小读取验证。
2. 生成候选 JSON，核对来源、去重、日期、字段与数量，保留现有数据快照。
3. 外部失败或空结果不能静默清空已发布内容。
4. 更新页面的来源与更新时间口径，运行校验和 Jekyll 预览。
5. 确认 Git diff 仅含可公开内容，按研究者要求发布。
## 2026-10-14 会话验证与 Frontier 接入更新

TopSight MCP 已在 Codex 会话内成功查询额度、检索及读取单篇论文。Frontier 已通过 `scripts/update_frontier_topsight.py` 转换经摘要相关性检查的结果，中文导读与历史机器译文分开标注。五大期刊未取得可收录的新记录，原站快照保持原日期；没有用其他来源冒充 TopSight 补齐。当前流程见 `frontier.md`。
