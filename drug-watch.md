---
layout: page
permalink: /drug-watch/index.html
title: Drug Watch
---

<link rel="stylesheet" href="/assets/css/drug-watch.css">
<script src="/assets/js/drug-watch.js" defer></script>

{% assign watch = site.data.drug_watch %}
{% assign categories = watch.categories %}
{% assign sources = watch.sources %}

<section class="drug-watch-meta">
  <p><strong>Update:</strong> `{{ watch.updated_at }}` (UTC)</p>
  <p class="drug-watch-note">{{ watch.maintainer_note }}</p>
</section>

<nav class="drug-watch-inline-toc">
  <h3>Quick Jump</h3>
  <ul>
    {% if categories and categories.size > 0 %}
    {% for category in categories %}
    <li><a href="#{{ category.id }}">{{ category.name }}</a></li>
    {% endfor %}
    {% endif %}
    <li><a href="#source-pool">Source Pool</a></li>
    <li><a href="#update-guide">Update Guide</a></li>
  </ul>
</nav>

<section class="drug-watch-intro">
  <h2>Innovative Drug Intelligence Tracker</h2>
  <p>This section tracks innovative-drug signals from daily news, latest academic studies, and latest industry research.</p>
  {% if watch.watch_keywords and watch.watch_keywords.size > 0 %}
  <p><strong>Watch keywords:</strong> {{ watch.watch_keywords | join: ", " }}</p>
  {% endif %}
</section>

{% if categories and categories.size > 0 %}
{% for category in categories %}
<section id="{{ category.id }}" class="drug-watch-section">
  <h2>{{ category.name }}</h2>
  {% if category.description %}
  <p class="drug-watch-section-desc">{{ category.description }}</p>
  {% endif %}

  {% if category.items and category.items.size > 0 %}
  {% for item in category.items %}
  <article class="drug-watch-item">
    <h3 class="drug-watch-item-title">
      {% if item.url %}
      <a href="{{ item.url }}">{{ item.title }}</a>
      {% else %}
      {{ item.title }}
      {% endif %}
    </h3>
    <p class="drug-watch-item-meta">
      {% if item.date %}<span>{{ item.date }}</span>{% endif %}
      {% if item.source %}<span> | {{ item.source }}</span>{% endif %}
      {% if item.platform %}<span> | {{ item.platform }}</span>{% endif %}
    </p>
    {% if item.summary %}
    <p class="drug-watch-item-summary">{{ item.summary }}</p>
    {% endif %}
    {% if item.tags and item.tags.size > 0 %}
    <p class="drug-watch-item-tags">Tags: {{ item.tags | join: ", " }}</p>
    {% endif %}
  </article>
  {% endfor %}
  {% else %}
  <p class="drug-watch-empty">No tracked items yet. Add entries in `_data/drug_watch.json`.</p>
  {% endif %}
</section>
{% endfor %}
{% endif %}

<section id="source-pool" class="drug-watch-section">
  <h2>Source Pool</h2>
  {% if sources and sources.size > 0 %}
  <ul class="drug-watch-sources">
    {% for source in sources %}
    <li>
      {% if source.url %}
      <a href="{{ source.url }}">{{ source.name }}</a>
      {% else %}
      {{ source.name }}
      {% endif %}
      {% if source.type %}
      <span class="drug-watch-source-type">({{ source.type }})</span>
      {% endif %}
    </li>
    {% endfor %}
  </ul>
  {% else %}
  <p>No sources configured.</p>
  {% endif %}
</section>

<section id="update-guide" class="drug-watch-section">
  <h2>Update Guide</h2>
  <ol>
    <li>Open `_data/drug_watch.json`.</li>
    <li>Set `updated_at` to the latest UTC timestamp.</li>
    <li>Add items under one of the three category `items` arrays.</li>
    <li>For each item, keep at least: `title`, `date`, `source`, `summary`, and optional `url`.</li>
  </ol>
</section>
