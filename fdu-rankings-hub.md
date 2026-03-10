---
layout: page
permalink: /blogs/fdu-rankings/index.html
title: 复旦周边评分系统总榜
---

<link rel="stylesheet" href="/assets/css/fdu-rankings-hub.css">
<script src="/assets/js/fdu-rankings-hub.js" defer></script>

<div class="rankings-hub-shell">
  <section class="rankings-hub-meta">
    <p><strong>说明：</strong>本页面汇总美食、咖啡、书店三类评分系统。各榜单按均值排序，数据来自同一 Firebase 仓库。</p>
    <p class="rankings-hub-note">后续你只需要维护这个入口页，不必在主页单独展示三个评分页面。</p>
  </section>

  <nav class="rankings-hub-toc">
    <h3>目录导航</h3>
    <ul>
      <li><a href="#hub-board-food">美食榜</a></li>
      <li><a href="#hub-board-coffee">咖啡榜</a></li>
      <li><a href="#hub-board-bookstore">书店榜</a></li>
    </ul>
  </nav>

  <section id="hub-board-food" class="rankings-hub-section">
    <h2>美食总榜</h2>
    <p class="rankings-hub-submeta">数据状态：<span id="hub-state-food">加载中...</span> | 更新时间：<span id="hub-updated-food">--</span></p>
    <p class="rankings-hub-link"><a href="/blogs/fdu-food-ranking/">进入美食评分页</a></p>
    <div class="rankings-hub-table-wrap">
      <table class="rankings-hub-table">
        <thead>
          <tr>
            <th>排名</th>
            <th>店铺</th>
            <th>区域</th>
            <th>均值</th>
            <th>评分数</th>
          </tr>
        </thead>
        <tbody id="hub-table-food"></tbody>
      </table>
    </div>
  </section>

  <section id="hub-board-coffee" class="rankings-hub-section">
    <h2>咖啡总榜</h2>
    <p class="rankings-hub-submeta">数据状态：<span id="hub-state-coffee">加载中...</span> | 更新时间：<span id="hub-updated-coffee">--</span></p>
    <p class="rankings-hub-link"><a href="/blogs/fdu-coffee-ranking/">进入咖啡评分页</a></p>
    <div class="rankings-hub-table-wrap">
      <table class="rankings-hub-table">
        <thead>
          <tr>
            <th>排名</th>
            <th>店铺</th>
            <th>区域</th>
            <th>均值</th>
            <th>评分数</th>
          </tr>
        </thead>
        <tbody id="hub-table-coffee"></tbody>
      </table>
    </div>
  </section>

  <section id="hub-board-bookstore" class="rankings-hub-section">
    <h2>书店总榜</h2>
    <p class="rankings-hub-submeta">数据状态：<span id="hub-state-bookstore">加载中...</span> | 更新时间：<span id="hub-updated-bookstore">--</span></p>
    <p class="rankings-hub-link"><a href="/blogs/fdu-bookstore-ranking/">进入书店评分页</a></p>
    <div class="rankings-hub-table-wrap">
      <table class="rankings-hub-table">
        <thead>
          <tr>
            <th>排名</th>
            <th>店铺</th>
            <th>区域</th>
            <th>均值</th>
            <th>评分数</th>
          </tr>
        </thead>
        <tbody id="hub-table-bookstore"></tbody>
      </table>
    </div>
  </section>
</div>

<script id="rankings-hub-seed" type="application/json">
{
  "boards": [
    {
      "key": "food",
      "name": "美食榜",
      "data": {{ site.data.fdu_food_ranking | jsonify }}
    },
    {
      "key": "coffee",
      "name": "咖啡榜",
      "data": {{ site.data.fdu_coffee_ranking | jsonify }}
    },
    {
      "key": "bookstore",
      "name": "书店榜",
      "data": {{ site.data.fdu_bookstore_ranking | jsonify }}
    }
  ]
}
</script>
