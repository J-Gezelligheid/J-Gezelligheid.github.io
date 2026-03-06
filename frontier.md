---
layout: page
permalink: /frontier/index.html
title: Frontier
---

<link rel="stylesheet" href="/assets/css/frontier-enhanced.css">
<script src="/assets/js/frontier-enhanced.js" defer></script>

{% assign t = site.data.frontier.translation %}
{% assign journals = site.data.frontier.journals %}
{% assign nber = site.data.frontier.nber %}

<section class="frontier-meta">
  <p><strong>Update:</strong> `{{ site.data.frontier.updated_at }}` (UTC)</p>
  {% if t and t.enabled == false %}
  <p class="frontier-note">Translation is disabled. Add `KIMI_API_KEY` in GitHub Actions Secrets.</p>
  {% endif %}
  {% if t and t.enabled %}
  <p class="frontier-note">Engine: {{ t.engine }} ({{ t.model }}), success={{ t.success_count | default: "N/A" }}, fail={{ t.fail_count | default: "N/A" }}</p>
  {% endif %}
</section>

<nav class="frontier-inline-toc">
  <h3>Quick Jump</h3>
  <ul>
    {% if journals and journals.size > 0 %}
    {% for journal in journals %}
    <li><a href="#journal-{{ forloop.index }}">{{ journal.name }}</a></li>
    {% endfor %}
    {% endif %}
    <li><a href="#nber-weekly">NBER Weekly</a></li>
    <li><a href="#frontier-feedback">Like & Comment</a></li>
  </ul>
</nav>

<section>
  <h2>Top-5 Economics Journals: Latest Issue TOC</h2>
  {% if journals and journals.size > 0 %}
  {% for journal in journals %}
  <section id="journal-{{ forloop.index }}" class="frontier-journal-section">
    <h3>{{ journal.name }}</h3>
    <p>Current issue: <a href="{{ journal.issue_url }}">{{ journal.issue_title }}</a></p>

    {% if journal.papers and journal.papers.size > 0 %}
    {% for paper in journal.papers limit: 12 %}
    <article class="frontier-paper">
      <h4 class="frontier-paper-en-title"><a href="{{ paper.url }}">{{ paper.title_en | default: paper.title }}</a></h4>
      <p class="frontier-paper-cn-title"><strong>CN Title:</strong> {{ paper.title_zh | default: "No Chinese translation yet." }}</p>
      <p class="frontier-paper-abstract frontier-paper-abstract-en"><strong>Abstract (EN):</strong> {{ paper.abstract_en | default: "No abstract available." }}</p>
      <p class="frontier-paper-abstract frontier-paper-abstract-zh"><strong>Abstract (ZH):</strong> {{ paper.abstract_zh | default: "No Chinese abstract available." }}</p>
    </article>
    {% endfor %}
    {% else %}
    <p>No article list captured in this run.</p>
    {% endif %}
  </section>
  {% endfor %}
  {% else %}
  <p>Data not available yet. Please run the updater once.</p>
  {% endif %}
</section>

<section id="nber-weekly" class="frontier-nber-section">
  <h2>NBER Working Papers (Last 7 Days)</h2>
  {% if nber and nber.papers and nber.papers.size > 0 %}
  {% for paper in nber.papers limit: 30 %}
  <article class="frontier-paper">
    <h4 class="frontier-paper-en-title">[{{ paper.id }}] <a href="{{ paper.url }}">{{ paper.title_en | default: paper.title }}</a>{% if paper.date %} ({{ paper.date }}){% endif %}</h4>
    <p class="frontier-paper-cn-title"><strong>CN Title:</strong> {{ paper.title_zh | default: "No Chinese translation yet." }}</p>
    <p class="frontier-paper-abstract frontier-paper-abstract-en"><strong>Abstract (EN):</strong> {{ paper.abstract_en | default: "No abstract available." }}</p>
    <p class="frontier-paper-abstract frontier-paper-abstract-zh"><strong>Abstract (ZH):</strong> {{ paper.abstract_zh | default: "No Chinese abstract available." }}</p>
  </article>
  {% endfor %}
  {% else %}
  <p>No NBER weekly updates captured in this run.</p>
  {% endif %}
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
