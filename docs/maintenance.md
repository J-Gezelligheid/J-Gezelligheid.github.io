# 主页维护指南

## 文件结构

站点采用 Jekyll 模板生成页面，没有 Node 构建流程。现有目录和 URL 保持不变，避免整理目录导致资源或链接失效。

| 路径 | 职责 |
| --- | --- |
| `index.md` | 个人介绍首页 |
| `publications.md` | 研究成果 |
| `Teaching & Research.md` | 教学与研究 |
| `_config.yml` | 作者信息、导航、站点生成配置 |
| `_layouts/`、`_includes/` | 公共模板、导航、页脚 |
| `_data/` | 栏目内容与结构化数据 |
| `assets/css/`、`assets/js/` | 样式与浏览器交互 |
| `scripts/` | 内容抓取和离线校验 |
| `blogs/`、`images/`、`firebase/` | 博客、图片、排名功能配置 |
| `backup/` | 原有备份，保留未移动 |
| `docs/` | 维护指南、来源说明、检查报告，不参与站点发布 |

## 更新入口

| 任务 | Drug Watch | Frontier |
| --- | --- | --- |
| 内容数据 | `_data/drug_watch.json` | `_data/frontier.json` |
| 页面结构 | `drug-watch.md` | `frontier.md` |
| 样式 | `assets/css/drug-watch.css` | `assets/css/frontier-enhanced.css` |
| 交互 | `assets/js/drug-watch.js` | `assets/js/frontier-enhanced.js` |
| 更新程序 | `scripts/update_drug_watch.py` | `scripts/update_frontier.py` |
| 固定 URL | `/drug-watch/` | `/frontier/` |
| 详细说明 | [drug_watch.md](drug_watch.md) | [frontier.md](frontier.md) |

`drug_watch` 是数据键和脚本命名；公开页面使用 `drug-watch`，两者不应统一重命名。

## 安装与离线检查

以下命令在仓库根目录执行，`python` 必须指向可运行的 Python 3。Windows Store 别名不代表已安装可用解释器。

```powershell
python scripts/validate_site.py
node --check assets/js/drug-watch.js
node --check assets/js/frontier-enhanced.js
```

校验脚本仅使用 Python 标准库，不抓取、不更改数据、不调用付费 API。错误退出码为 1；日期过旧、采集失败、翻译缺失等告警须人工审阅。它不替代 Jekyll 构建、链接在线可达性或文献真实性核查。

需要实际抓取时，在独立虚拟环境安装依赖：

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

依赖清单来自现有代码的 imports，尚未锁定版本或执行联网安装。

## 每次内容更新流程

1. 读取 `STATE.md`、`TASKS.md`，明确栏目、时间范围、来源和展示要求。
2. 用 `git status --short` 核对工作区，为已有未提交数据创建快照。

```powershell
$snapshotPath = Join-Path '.local/snapshots' (Get-Date -Format 'yyyyMMdd-HHmmss-fff')
New-Item -ItemType Directory -Path $snapshotPath -ErrorAction Stop
Copy-Item -LiteralPath '_data/drug_watch.json','_data/frontier.json' -Destination $snapshotPath
```

3. 按栏目指南编辑 JSON 或运行抓取脚本。现有脚本直接覆盖对应 JSON，不提供 dry-run；人工新增内容也可能被下次抓取替换。
4. 执行离线检查，查看 `git diff -- _data/`；逐项核对新增链接、日期、重复项、摘要和翻译，不把抓取时间当成来源更新时间。
5. 涉及页面变更时，用可用的 Ruby/Jekyll 环境构建预览，检查桌面和移动端、锚点和交互。本次未建立 Ruby 环境，也未验证完整构建。
6. 更新 `STATE.md`、`TASKS.md`、`CHANGELOG.md`，提交审查后的修改，再按研究者发布要求同步 GitHub。

## 自动更新现状

复制基线没有 `.github/workflows/`，没有 `Gemfile` 或依赖锁文件。存在抓取脚本并不代表定时更新已启用。GitHub 仓库的 Pages 设置、Secrets 与外部自动任务没有随 Git clone 复制，也未查询验证。

后续建议先完善失败保护、日志和可审查输出，再增加手动触发和定时工作流。不要在整理阶段直接部署未经核实的新数据。

## 来源与回溯

- 原本地目录：`D:/Academic/Personal/website/J-Gezelligheid.github.io`
- GitHub 上游：`https://github.com/J-Gezelligheid/J-Gezelligheid.github.io.git`
- 原基线：`1260857ecbdfe38a716afee0baea18106a653382`，15 次提交。
- 新工作目录：`D:/EconResearchOS/projects/personal_homepage`
- 维护分支：`codex/homepage-maintenance`。
- 原 README 留存于 [original_readme.md](original_readme.md)，原版本也可通过 Git 历史查看。
- 本仓库有独立 `.git`，Git 操作应在此目录执行；本轮没有在 EconResearchOS 根仓库中添加嵌套仓库或 submodule。
