# CHANGELOG
## 2026-11-02 五刊卷期修正

发布验证：内容提交 69f5c1400c1f1e03b14d14ff39be11452bcd76b7；Pages run 41372949218。线上五刊卷期标签和全部 63 个研究论文题名已逐项匹配，21 篇工作论文保留。11 项测试与 Liquid 渲染通过。月度自动化已更新为官网先核验，再同步目录。


期刊最新目录以出版社官网为准；TopSight 主题检索不再充当卷期发现流程。已核验 AER 116(11)、JPE 134(10)、QJE 141(4)、REStud 93(5)、Econometrica 94(5)。官方卷期链接及研究论文数量见 docs/frontier_issues_20261102.json。

每月先逐一访问五刊官网 current issue / issues，形成当日核验清单（volume、issue、year、month、issue_url、expected_count、verified_on）；检查新旧卷期，不能把空检索视为“期刊没有更新”。执行 scripts/update_frontier_journals.py --manifest 当日清单 --cache .local/当日目录，按明确卷期筛选全部研究论文并核对数量，排除 Front Matter、Referees、Turnaround Times。Crossref 必须回溯早期在线文章，不能只筛当前年份，否则漏掉已编入新卷期的旧在线记录。若官网或 DOI 元数据不可用，保留旧数据并报告未完成，不报告五刊更新成功。工作论文继续 TopSight。不能把出版社目录冒充 TopSight 结果。

本次 63 篇目录记录仅同步元数据，缺失摘要/中文译文如实标注并提供 DOI 原文链接。旧数据保存在 .local 快照与 Git 历史。发布后核对实际 Pages 产物。ChatGPT 安全连接需要重连，当前所需浏览器接口不可用，未声称完成网页审查；CORDIS 工具未暴露。


## 2026-11-01

### Added
- 本月选文审查清单 frontier_selection_20261101.json；14 次检索记录保存在忽略目录。
### Changed
- 劳动、宏观、发展主题换入 8 篇论文，替换 7 篇；当前 21 篇工作论文。
### Fixed
- 无代码变更。
### Notes
- 其余 6 个主题、五刊和 NBER 保留原内容与日期；五刊仍无可收录新结果。仅摘要相关性审查，非全文核验。8 项测试通过，数据检查 0 错误。
- ChatGPT 连接健康，但所需浏览器接口不可用，未执行网页审查；CORDIS 工具未暴露。
### Next
- 内容提交 99acde2 的 Pages run 41291635989 已成功；线上 21 篇题名、9 组主题、CSS/JS 与交互均核对通过。下月继续检查五刊来源。

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
- 提交 `7e55d84` 已普通快进发布至原 main；GitHub Pages run `38500020595` 构建/部署成功。线上实际 Jekyll 产物包含全部 20 个选文题名，9 组主题；线上 CSS/JS 与本地一致，交互检查通过。
- 五刊定向检索未取得可收录新记录，部分外部通道超时；保留原日期并公开通道状态。
- CORDIS 工具未在会话暴露，以本地证据与本记录留痕；密钥与原始返回未纳入提交。

### Next

- 月度更新继续检查五刊来源可用性；浏览器工具恢复后补截图级视觉复核，后续接入 Drug Watch。

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
