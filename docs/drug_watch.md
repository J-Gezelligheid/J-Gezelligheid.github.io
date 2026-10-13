# Drug Watch 维护说明

后续数据源已确定为 Gmail，连接状态与接入要求见 [source_integration.md](source_integration.md)。以下说明记录目前仓库已有实现。

## 数据契约

`drug-watch.md` 通过 `site.data.drug_watch` 读取 `_data/drug_watch.json`。

| 字段 | 含义 |
| --- | --- |
| `updated_at` | 脚本运行时间，UTC；不等于每条来源的新鲜度 |
| `maintainer_note` | 页面说明 |
| `watch_keywords` | 页面显示关键词；修改它不会自动修改检索 query |
| `categories` | 三个栏目，固定 ID 为 `daily-news`、`latest-research`、`industry-research` |
| `categories[].items[]` | `title`、`date`、`source`、`platform`、`url`、`summary`、`tags` |
| `sources` | 页面展示的来源池，不代表已经为每个平台实现了采集 |
| `fetch` | 采集参数、各源数量与错误、旧数据回退标记 |

日期采用 `YYYY-MM-DD`，条目应附可核实原始链接；`url` 当前模板允许为空，校验会提示缺失。

## 现有采集链路

- PubMed E-utilities：检索论文、获取元数据与摘要。
- Google News RSS：抓取资讯和产业线索，按英文关键词筛选。
- 腾讯混元 API：可选的联网检索结构化摘要；脚本命名为 Yuanbao，但实际 HTTP 请求发往 `HUNYUAN_API_BASE`。
- 按 URL / 标题去重；某类没有新条目时退回该类旧数据；所有栏目均为空时终止写入。

“Source Pool”中的微信、微博、知乎等名称不代表独立官方 API 抓取已经实现。AI 返回的内容与链接需要逐条核验。

## 运行配置

| 环境变量 | 现有默认值 / 用途 |
| --- | --- |
| `DRUG_WATCH_WINDOW_DAYS` | `7` |
| `DRUG_WATCH_TIMEOUT_SECONDS` | `35` |
| `DRUG_WATCH_MAX_DAILY_NEWS` / `DRUG_WATCH_MAX_LATEST_RESEARCH` / `DRUG_WATCH_MAX_INDUSTRY_RESEARCH` | 各 `24` |
| `DRUG_WATCH_MAX_PUBMED_ITEMS` / `DRUG_WATCH_MAX_RSS_ITEMS_PER_QUERY` | 各 `18` |
| `DRUG_WATCH_MAX_YUANBAO_ITEMS_PER_CATEGORY` | `10` |
| `DRUG_WATCH_PUBMED_QUERY` | 覆盖 PubMed 查询 |
| `DRUG_WATCH_NEWS_QUERY_EN` / `DRUG_WATCH_INDUSTRY_QUERY_EN` | 覆盖资讯 / 产业查询 |
| `DRUG_WATCH_ENABLE_YUANBAO` | `true`；无 key 时可选 API 不启用 |
| `HUNYUAN_API_KEY` / `TENCENT_YUANBAO_API_KEY` | 环境变量提供 key，前者优先 |
| `HUNYUAN_API_BASE` / `HUNYUAN_MODEL` | 当前代码默认混元 API 与 `hunyuan-turbos-latest`；可用性待联网验证 |

按维护指南先备份，再运行以下命令可关闭可选 AI 服务，仅调用 PubMed / RSS：

```powershell
$env:DRUG_WATCH_ENABLE_YUANBAO = 'false'
.\.venv\Scripts\python.exe scripts/update_drug_watch.py
.\.venv\Scripts\python.exe scripts/validate_site.py
git diff -- _data/drug_watch.json
```

脚本不自动读取 `.env`。不要把 key 写入代码或提交。

## 后续优先事项

1. 补充类别级的成功时间和回退状态展示，避免旧数据看起来刚刚更新。
2. 明确研究者关注的国家、监管机构、疾病、技术路线与事件类型，调整实际查询和筛选规则。
3. 区分人工内容和自动采集内容，防止人工整理被覆盖。
4. 增加可审查的候选输出、原始来源留痕和自动运行记录。
5. 当前 JSON 的 `maintainer_note` 标注 Manual curation，而 `fetch` 中存在自动采集元数据，更新时需澄清。

本轮仅整理，未抓取新资讯、未改写现有内容。
