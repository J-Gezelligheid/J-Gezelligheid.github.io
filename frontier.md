---
layout: page
permalink: /frontier/index.html
title: Frontier
---

<link rel="stylesheet" href="/assets/css/frontier-enhanced.css">
<script src="/assets/js/frontier-enhanced.js" defer></script>

{% assign frontier = site.data.frontier %}
{% assign journals = frontier.journals %}
<header class="frontier-hero" lang="zh-CN">
  <p class="frontier-eyebrow">ECONOMICS · RESEARCH FRONTIER</p>
  <h1>经济学前沿</h1>
  <p class="frontier-lead">从五大期刊到工作论文，追踪问题、方法与新的研究线索。</p>
  <p class="frontier-source">本页更新：{{ frontier.updated_at | date: '%Y-%m-%d' }} · 每月更新 · 各栏目来源日期单独标注</p>
  <nav class="frontier-jumps" aria-label="Frontier sections">
    <a href="#working-papers">本期工作论文</a><a href="#top-five">五大期刊</a><a href="#nber-weekly">往期 NBER</a><a href="#frontier-method">来源说明</a>
  </nav>
</header>

<section id="working-papers" lang="zh-CN">
  <h2>工作论文 · 主题选读</h2>
  <p>涵盖劳动、贸易、宏观、发展、产业组织、公共经济学、计量、理论与行为经济学。{{ frontier.working.window_note | escape }}。中文导读由 TopSight 提供，不替代原文与识别策略核查。</p>
  <div class="frontier-tools" hidden>
    <label for="frontier-search">搜索题名、作者或关键词</label>
    <input type="search" id="frontier-search" placeholder="例如：trade、AI、税收" autocomplete="off">
    <label for="frontier-topic">主题</label>
    <select id="frontier-topic"><option value="all">全部主题</option>{% for topic in frontier.working.topics %}<option value="{{ topic.id | escape }}">{{ topic.label | escape }}</option>{% endfor %}</select>
    <p id="frontier-result-count" role="status" aria-live="polite"></p>
  </div>
  <p id="frontier-no-results" hidden>未找到匹配的论文，请尝试其他关键词或主题。</p>
  {% for topic in frontier.working.topics %}
  <section class="frontier-topic-section" data-frontier-topic id="topic-{{ topic.id | escape }}">
    <h3>{{ topic.label | escape }} <span class="frontier-count">{{ topic.papers.size }}</span></h3>
    <p class="frontier-source">{% if topic.status == 'retained' %}本次未取得可用更新，保留往期选文。{% endif %}{% if topic.updated_at %}收录日期：{{ topic.updated_at | date: '%Y-%m-%d' }}{% else %}本次尚无可收录记录。{% endif %}</p>
    {% for paper in topic.papers %}{% include frontier-paper.html paper=paper topic=topic.id %}{% endfor %}
  </section>
  {% endfor %}
</section>

<section id="top-five" lang="zh-CN">
  <h2>五大经济学期刊</h2>
  <p class="frontier-notice">按期刊展示检索选文；未取得可用更新的栏目保留历史快照，并标注各自收录日期。历史卷期不代表当前最新一期。</p>
  {% for journal in journals %}
  <section id="journal-{{ forloop.index }}" class="frontier-journal-section">
    <h3>{{ journal.name | escape }}</h3>
    <p class="frontier-source">{{ journal.source | escape }} · 收录：{{ journal.updated_at | date: '%Y-%m-%d' }}{% if journal.status == 'retained' %} · 历史快照{% endif %}</p>
    <p><a href="{{ journal.issue_url | escape }}">期刊主页</a> · {{ journal.issue_title | escape }}</p>
    <details class="frontier-issue"><summary>展开研究论文</summary>
    {% for paper in journal.papers %}{% unless paper.is_research == false %}{% include frontier-paper.html paper=paper topic='journal' %}{% endunless %}{% endfor %}
    </details>
  </section>
  {% endfor %}
</section>

<section id="nber-weekly" class="frontier-nber-section" lang="zh-CN">
  <h2>NBER · 往期存档</h2>
  <p class="frontier-source">原站 NBER 快照 · {{ frontier.nber.updated_at | date: '%Y-%m-%d' }} · {{ frontier.nber.papers.size }} 篇。保留供回看；当前工作论文见上方主题选读。</p>
  <details class="frontier-issue"><summary>展开往期 NBER 论文</summary>
  {% for paper in frontier.nber.papers %}{% include frontier-paper.html paper=paper topic='archive' %}{% endfor %}
  </details>
</section>

<section id="frontier-method" class="frontier-method" lang="zh-CN">
  <h2>来源与阅读说明</h2>
  <p>本期工作论文来自 <a href="https://topsight.net/">TopSight</a> 的主题检索，经摘要层面的相关性检查后选入。检索覆盖有限候选池，不构成完整文献清单，也不代表已完成全文核验。工作论文可能继续修订，引用时请核对作者与版本。</p>
  <p>中文题名与导读为来源提供的辅助阅读内容；历史期刊栏目保留原站机器译文。模型推论、相关性结果和因果识别的适用条件请以英文原文为准。缺少原文链接的记录保留题名、作者及来源编号，不补造链接。</p>
  <details><summary>本次检索通道状态</summary>
    <ul>{% for check in frontier.source_checks %}<li>{{ check.term | escape }}{% if check.journal and check.journal != '' %} · {{ check.journal | escape }}{% endif %}：{% if check.ok %}{% for lane in check.lanes %}{{ lane[0] | escape }} / {{ lane[1].status | escape }}{% unless forloop.last %}；{% endunless %}{% endfor %}{% else %}请求失败{% endif %}</li>{% endfor %}</ul>
    <p>complete 表示本次请求成功，不表示收录完整；empty 表示未返回记录；failed 表示该通道暂不可用。非五大期刊结果不纳入期刊栏目。原站 Crossref / OpenAlex / NBER 快照与本次 TopSight 结果分开展示。</p>
  </details>
</section>

<section id="frontier-feedback" class="frontier-feedback">
  <h2>Feedback</h2>
  <p>Lightweight local comment area. Likes and comments are saved in your browser only.</p>

  <button type="button" id="frontier-like-btn" class="frontier-like-btn">Like <span id="frontier-like-count">0</span></button>

  <form id="frontier-comment-form" class="frontier-comment-form">
    <label for="frontier-comment-input">Comment</label>
    <textarea id="frontier-comment-input" rows="4" maxlength="600" placeholder="Write your thoughts..."></textarea>
    <button type="submit">Post Comment</button>
  </form>

  <ul id="frontier-comment-list" class="frontier-comment-list"></ul>
</section>
