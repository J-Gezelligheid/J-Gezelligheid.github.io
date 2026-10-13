# STATE

## 当前阶段

2026-10-13：已完成独立仓库复制与维护入口整理，下一阶段为 Gmail / TopSight 接入。

## 来源

- 原目录：`D:/Academic/Personal/website/J-Gezelligheid.github.io`
- 上游：`https://github.com/J-Gezelligheid/J-Gezelligheid.github.io.git`
- 复制基线：`1260857`（`main`）；复制前原工作区干净。
- 当前目录：`D:/EconResearchOS/projects/personal_homepage`

## 优先级与下一步

1. Gmail 连接完成后，核对药物资讯邮件的 label / 发送者和时间窗口，生成 Drug Watch 候选内容。
2. 获取 TopSight API 文档并完成最小读取验证，再实现 Frontier 转换器。
3. 解决来源失败保护和更新时间口径，随后构建预览。

## 已完成

- 保留完整历史（复制基线共 15 次提交），建立 `codex/homepage-maintenance` 分支，origin 指向原 GitHub 上游。
- 补齐维护文档、Python 依赖清单、Git 忽略规则、Jekyll 维护文件排除规则。
- 新增标准库离线校验脚本；现有数据结构、页面资源引用和 Python / 两个栏目 JS 语法检查通过。
- 数据仍为 2026-03-06 快照：Drug Watch 50 条；Frontier 54 篇期刊论文 + 27 篇 NBER；15 篇期刊论文缺少中英文摘要。
- 现有公开页面、栏目 JSON 和原有采集脚本保持复制基线。

## 限制

- Gmail 插件尚未确认安装 / 连接；待研究者完成账户连接。
- TopSight 官网接入文档匿名访问返回 401；待 API 文档 / 示例，密钥未写入文件且未测试有效性。
- 本机 PATH 未发现 Ruby / Bundler；默认 Python 为不可执行的 Windows Store 别名。已使用 Codex 附带 Python 3.12 执行标准库检查，其环境缺少 requests；尚未安装抓取依赖或运行抓取脚本。
- 未完成 Jekyll 实际构建或视觉预览，未修改线上站点、未推送 GitHub、未创建远端新仓库。
- 当前会话未暴露 CORDIS MCP 工具，改用本地检查报告与变更记录留痕。
