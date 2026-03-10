---
layout: page
permalink: /blogs/fdu-food-ranking/index.html
title: 复旦周边美食评分排行榜
---

<link rel="stylesheet" href="/assets/css/fdu-food-ranking.css">
<script src="/assets/js/fdu-food-ranking.js" defer></script>

{% assign board = site.data.fdu_food_ranking %}

<div class="food-board-shell">
  <section class="food-board-meta">
    <p><strong>更新时间：</strong> `{{ board.updated_at }}` (UTC)</p>
    <p class="food-board-note">支持国权路、三号湾、五角场三个区域。你可以自行新增店铺，所有已记录评分按均值自动更新总榜。</p>
    <p id="food-board-store-mode" class="food-board-mode"></p>
  </section>

  <nav class="food-board-inline-toc">
    <h3>快速跳转</h3>
    <ul>
      <li><a href="#food-board-ranking">总榜（均值）</a></li>
      <li><a href="#food-board-rate">我要评分</a></li>
      <li><a href="#food-board-add-shop">添加店铺</a></li>
      <li><a href="#food-board-area">分区域看板</a></li>
      <li><a href="#food-board-manage">维护说明</a></li>
    </ul>
  </nav>

  <section id="food-board-ranking" class="food-board-section">
    <h2>总榜（按均值排序）</h2>
    <div class="food-table-wrap">
      <table class="food-ranking-table">
        <thead>
          <tr>
            <th>排名</th>
            <th>店铺</th>
            <th>区域</th>
            <th>均值</th>
            <th>评分数</th>
          </tr>
        </thead>
        <tbody id="food-ranking-table-body"></tbody>
      </table>
    </div>
  </section>

  <section id="food-board-rate" class="food-board-section">
    <h2>我要评分</h2>
    <form id="food-rating-form" class="food-board-form">
      <label for="food-rating-shop">店铺</label>
      <select id="food-rating-shop" required></select>

      <label for="food-rating-score">评分（1-5）</label>
      <select id="food-rating-score" required>
        <option value="5">5 - 非常推荐</option>
        <option value="4">4 - 值得去</option>
        <option value="3">3 - 一般</option>
        <option value="2">2 - 不太推荐</option>
        <option value="1">1 - 不推荐</option>
      </select>

      <label for="food-rating-user">昵称（可选）</label>
      <input id="food-rating-user" type="text" maxlength="30" placeholder="匿名可留空">

      <button id="food-rating-submit" type="submit">提交评分</button>
    </form>
    <p id="food-rating-message" class="food-board-message" aria-live="polite"></p>
  </section>

  <section id="food-board-add-shop" class="food-board-section">
    <h2>添加店铺</h2>
    <form id="food-add-shop-form" class="food-board-form">
      <label for="food-add-shop-area">所属区域</label>
      <select id="food-add-shop-area" required></select>

      <label for="food-add-shop-name">店铺名</label>
      <input id="food-add-shop-name" type="text" maxlength="40" placeholder="例如：某某小馆" required>

      <label for="food-add-shop-owner">提交人（可选）</label>
      <input id="food-add-shop-owner" type="text" maxlength="30" placeholder="方便后续追踪可填写">

      <button id="food-add-shop-submit" type="submit">添加店铺</button>
    </form>
    <p id="food-add-shop-message" class="food-board-message" aria-live="polite"></p>
  </section>

  <section id="food-board-area" class="food-board-section">
    <h2>分区域看板</h2>
    <div id="food-area-grid" class="food-area-grid"></div>
  </section>

  <section id="food-board-manage" class="food-board-section">
    <h2>维护说明</h2>
    <ol>
      <li>已启用 Firebase 共享模式；若配置不完整，页面会自动回退到本地模式。</li>
      <li>请在 <code>_data/fdu_food_ranking.json</code> 填写真实 <code>database_url</code> 与 <code>api_key</code>（不要保留 <code>REPLACE_WITH_*</code> 占位符）。</li>
      <li>Firebase Console 中需开启 Realtime Database 与 Anonymous Authentication。</li>
      <li>将 <code>firebase/fdu_food_ranking.database.rules.json</code> 的规则粘贴到 Realtime Database Rules 页面后发布。</li>
      <li>完整上线步骤见仓库文档：<code>firebase/FDU_FOOD_RANKING_SETUP.md</code>。</li>
      <li>共享模式下，页面会把新增店铺与评分写入 Firebase 的 <code>data_root</code> 节点，并自动按所有评分均值聚合。</li>
    </ol>
  </section>
</div>

<script id="food-ranking-seed" type="application/json">{{ board | jsonify }}</script>
