# Frontier 维护说明

## 当前流程（2026-10-14）

当前页面使用 TopSight 主题选文，并保留原站五大期刊与 NBER 历史快照。**不要再运行旧 `scripts/update_frontier.py` 覆盖 v2 数据**；该脚本仅保留为历史实现。

- 新入口：`scripts/update_frontier_topsight.py`；检索计划：`scripts/frontier_plan.json`。
- 9 个综合经济学主题 + 5 个期刊定向请求，通常每轮 14 次检索；先查询额度，额度不足停止，不无限重试。每次一条核心短语、三库分通道；外部通道失败时可单独重试一次。
- 当前选文 20 篇，依据英文摘要检查相关性；选择记录见 `frontier_selection_20261014.json`。这是摘要层面选文，不是全文审查。
- 五大期刊定向请求本次未取得可用记录；部分外部通道超时。保留 2026-03-06 的 54 条期刊记录（页面隐藏 Front Matter 等非研究条目）和 27 篇 NBER，不能称为当前最新一期或最近七天。
- `summary_zh` 是 TopSight 中文导读；`abstract_zh` 仅用于历史机器译文，两者不能混用。缺失 URL 时保留来源编号，不猜链接。来源的出版日可能含月首/年首占位，页面只展示年份和实际收录日。

### 每月操作

研究者已授权 **每月 1 日 09:00（Asia/Shanghai）更新并自动发布至原 GitHub 主页**。已创建当前聊天的 heartbeat，ID `frontier`，状态 ACTIVE。运行依赖本机 Codex 开启、网络和现有 GitHub 凭据可用；不得报告尚未完成的部署。

1. 读取项目规则、STATE、TASKS。检查 `git status`；若有不属于本任务的修改，保留并停止自动发布。`git fetch origin main`，确保本地与上游可正常快进；分叉则停止，不强推、不覆盖远端修改。
2. 使用 TopSight MCP 查询额度并按计划检索；或者使用已安装客户端的 Python 执行下方 `--fetch`。MCP 结果保存为忽略目录 `.local/frontier/batch-YYYYMMDD.json`，形如 `{retrieved_at, queries:[{topic, request, response}]}`；只保存 structuredContent。不得保存密钥、Gmail 数据或 GitHub 凭据。
3. 阅读返回英文摘要，按主题选 2–3 篇相关论文，期刊只接收指定五刊，外部通道只接收 core。不因凑数选入泛词命中记录；不将其他期刊或外部网页混入 TopSight 五刊结果。期刊或主题空结果/失败时不清空旧数据。
4. 创建本次 `docs/frontier_selection_YYYYMMDD.json`，包含 `reviewed:true`、`review_basis`、`topics:{主题id:[paper_key]}`、`journals:{期刊全名:[paper_key]}`。空列表代表保留上一批。判断重复时比对 DOI / 题名，不只是 key。对比上一期：如果只有抓取日期变化、无新选文或实质元数据修正，保留公开数据，不做无意义发布。
5. 运行转换器 `--batch ... --selections ...`，自动留快照。运行标准库检查与安全测试、`node --check assets/js/frontier-enhanced.js`。核对中英文内容、来源归属、日期、缺失链接和源错误；维护日志。所有外部文本必须通过 Liquid `escape` 输出。
6. 审查 `git diff` 与将提交文件，确保无密钥/账号私密信息。只提交本轮维护文件；再次检查远端，使用 `git push origin HEAD:main` 普通快进推送。禁止 force push。用户已授权发布，无需再询问。
7. 检查 GitHub Pages 对应 SHA 构建完成，打开 `/frontier/` 验证日期、论文、主题筛选和摘要。构建失败先修复再普通提交；不要将仅 push 成功当作部署成功。仅在发布完成、失败或需要用户处理时通知；无变化保持安静。

本机 Git 直连 GitHub 超时，而系统代理可用。可用 `python scripts/git_with_system_proxy.py fetch origin main` / `python scripts/git_with_system_proxy.py push origin HEAD:main` 临时沿用现有系统代理；不改变 Git 或系统设置，也不打印代理凭据。

```powershell
# Fetch: 使用安装包的独立环境；客户端读取 Codex 配置中的私密 key 文件路径。
& "$env:USERPROFILE/.codex/mcp/topsight-literature/0.3.4/.venv/Scripts/python.exe" -B scripts/update_frontier_topsight.py --fetch .local/frontier/batch-YYYYMMDD.json
# 下列转换与检查仅依赖 Python 标准库，可用 Codex 内置 Python。
python scripts/update_frontier_topsight.py --batch .local/frontier/batch-YYYYMMDD.json --selections docs/frontier_selection_YYYYMMDD.json
python scripts/validate_site.py
python -m unittest discover -s tests -v
node --check assets/js/frontier-enhanced.js
```

### v2 数据契约

保留原 `journals` / `nber` / `translation`，新增 `schema_version:2`、`checked_at`、`working.topics[]`、`source_checks[]`。各分组 `updated_at` 表示该组收录成功时间；失败保留旧日期。`source_checks` 仅含公开的查询、通道状态与计数。源响应和快照只在 `.local`，不发布。

论文白名单字段包括 key、题名、中英文阅读内容、作者、年份、来源编号、DOI / URL、来源通道、主题、收录日；原始 client、quota、密钥字段不能进入公开 JSON。

以下是 **复制基线的历史实现说明**，不作为当前更新入口。

## 数据契约

`frontier.md` 通过 `site.data.frontier` 读取 `_data/frontier.json`。

| 字段 | 含义 |
| --- | --- |
| `updated_at` | 脚本运行时间；现有字符串无时区后缀，代码以 UTC 生成 |
| `translation` | Kimi 模型、启用状态、请求成功 / 失败数和失败示例 |
| `journals[]` | `name`、`issue_title`、`issue_url`、`papers`、`error` |
| `nber` | `source`、`window_days`、`papers`、`error` |
| `papers[]` | `title_en`、`title_zh`、`url`、`abstract_en`、`abstract_zh`；NBER 另含 `id`、`date` |

现有期刊为 AER、JPE、QJE、REStud、Econometrica。页面每刊最多显示 12 篇、NBER 最多 30 篇；调整脚本数量上限时须同步检查页面 Liquid 的 `limit`。

## 现有采集链路

1. Crossref：每刊读取按 published 倒序的 120 条记录，选首个带卷期的 journal-article 的卷期，再取匹配条目。
2. OpenAlex：Crossref 缺摘要时尝试通过 DOI 补充。
3. NBER：使用 API 的 `newthisweek` 标记筛选，未自行按日期计算滚动七天。
4. Kimi：翻译标题和摘要，旧 JSON 的英文—中文文本对用作缓存。

这是现有代码行为说明，未联网核实各接口当前可用性。Crossref 元数据选出的卷期与官网最新目录是否一致，需要核对。

## 运行配置

| 环境变量 | 现有默认值 / 用途 |
| --- | --- |
| `KIMI_API_KEY` | 空；无 key 时不请求新翻译，可复用已有缓存 |
| `KIMI_API_BASE` | `https://api.moonshot.cn/v1` |
| `KIMI_MODEL` | `moonshot-v1-8k`，可用性待联网验证 |
| `KIMI_MIN_INTERVAL_SECONDS` | `3.2` |
| `MAX_ABSTRACT_TRANSLATE_CHARS` | `2500`，超长英文摘要截断后翻译 |
| `MAX_PAPERS_PER_JOURNAL` | `12` |
| `MAX_NBER_PAPERS` | `30` |

按维护指南先备份，配置环境变量后运行：

```powershell
.\.venv\Scripts\python.exe scripts/update_frontier.py
.\.venv\Scripts\python.exe scripts/validate_site.py
git diff -- _data/frontier.json
```

脚本不自动读取 `.env`。

## 后续优先事项

1. 增加分来源失败保护。当前抓取异常变为 `error` 与空列表；例如未启用翻译时，可能将已有内容覆盖为空。页面目前也不展示这些 `error`。
2. 修正翻译成功判断：启用 Kimi 且 `success_count == 0` 就报错，而全部命中缓存时同样可能为零；缓存成功与新请求成功应分开计数。
3. 统一 NBER 页面的 “Last 7 Days” 与代码的 `newthisweek` 口径。
4. 为长摘要翻译增加截断说明；完整原文与截断译文不能被当成等长对照。
5. 改善去重、来源成功时间、人工选文和归档流程。
6. 点赞与评论目前仅写入当前浏览器 `localStorage`，不是跨用户共享留言；后续按需求决定是否保留。

本轮仅整理，未抓取新论文、未生成新翻译、未改写现有内容。
