# STATE

## 当前阶段

2026-10-14：仓库整理已完成；TopSight 本地 MCP 已安装、实测并合并配置，等待 Codex 完全退出重开后的新会话加载。下一阶段为两个栏目内容接入。

## 来源

- 原目录：`D:/Academic/Personal/website/J-Gezelligheid.github.io`
- 上游：`https://github.com/J-Gezelligheid/J-Gezelligheid.github.io.git`
- 复制基线：`1260857`（`main`）；复制前原工作区干净。
- 当前目录：`D:/EconResearchOS/projects/personal_homepage`

## 优先级与下一步

1. 完全退出并重新打开 Codex，新建任务先发送“请查看我的顶见文献 API 额度，不要执行检索。”。
2. 核对 Gmail 药物资讯邮件的 label / 发送者和时间窗口，生成 Drug Watch 候选内容；根据 TopSight 实际数据结构实现 Frontier 转换器。
3. 解决来源失败保护和更新时间口径，随后构建预览。

## 已完成

- 保留完整历史（复制基线共 15 次提交），建立 `codex/homepage-maintenance` 分支，origin 指向原 GitHub 上游。
- 补齐维护文档、Python 依赖清单、Git 忽略规则、Jekyll 维护文件排除规则。
- 新增标准库离线校验脚本；现有数据结构、页面资源引用和 Python / 两个栏目 JS 语法检查通过。
- 数据仍为 2026-03-06 快照：Drug Watch 50 条；Frontier 54 篇期刊论文 + 27 篇 NBER；15 篇期刊论文缺少中英文摘要。
- 现有公开页面、栏目 JSON 和原有采集脚本保持复制基线。

## 限制

- Gmail 已由研究者确认安装，Gmail 工具已在会话中出现；尚未读取邮件。
- TopSight 三工具在独立 MCP 客户端中实测通过；新配置尚待重启后的 Codex 新会话加载验证。详情见 `docs/source_integration.md`。
- 本机 PATH 未发现 Ruby / Bundler；默认 Python 为不可执行的 Windows Store 别名。已使用 Codex 附带 Python 3.12 执行标准库检查，其环境缺少 requests；尚未安装抓取依赖或运行抓取脚本。
- 未完成 Jekyll 实际构建或视觉预览，未修改线上站点、未推送 GitHub、未创建远端新仓库。
- 当前会话未暴露 CORDIS MCP 工具，改用本地检查报告与变更记录留痕。
