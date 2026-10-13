# Frontier 维护说明

后续数据源已确定为 TopSight，接口文档与接入要求见 [source_integration.md](source_integration.md)。以下说明记录目前仓库已有实现。

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
