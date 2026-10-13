# Personal Homepage Agent Rules

- 遵循 `D:/EconResearchOS/AGENTS.md`；默认使用简体中文交流，代码和文件名使用英文。
- 开始任务前读取本文件、`README.md`、`STATE.md`、`TASKS.md` 和相关栏目维护说明。
- 这是个人主页的独立 Git 仓库，技术栈为 Jekyll / GitHub Pages；保留现有 URL、主题和栏目数据契约。
- 优先维护 `drug-watch.md`、`frontier.md` 及其 `_data/`、`assets/`、`scripts/` 文件。
- 数据抓取脚本会写入现有 JSON；运行前保留快照，运行后核对来源、日期、数量、失败和回退情况。
- 不将 API key 写入代码、数据、文档或提交；通过环境变量或 GitHub Secrets 配置。
- 未核实的资讯和论文信息不得写成已确认事实；区分原文、机器摘要和机器翻译。
- 维护文档与日志不应作为公开站点页面发布，应纳入 Jekyll `exclude`。
- 重大修改更新 `STATE.md`、`TASKS.md`、`CHANGELOG.md`；部署前先完成检查并审查 diff。
