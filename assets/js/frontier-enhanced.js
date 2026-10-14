(function () {
  const likeKey = "frontier_like_count_v1";
  const commentsKey = "frontier_comments_v1";

  function getComments() {
    try {
      const raw = localStorage.getItem(commentsKey);
      const arr = raw ? JSON.parse(raw) : [];
      return Array.isArray(arr) ? arr : [];
    } catch (_) {
      return [];
    }
  }

  function saveComments(comments) {
    try { localStorage.setItem(commentsKey, JSON.stringify(comments)); return true; }
    catch (_) { return false; }
  }

  function renderComments() {
    const list = document.getElementById("frontier-comment-list");
    if (!list) return;

    const comments = getComments();
    list.innerHTML = "";

    if (!comments.length) {
      const empty = document.createElement("li");
      empty.className = "frontier-comment-empty";
      empty.textContent = "No comments yet. Be the first to post.";
      list.appendChild(empty);
      return;
    }

    comments
      .slice()
      .reverse()
      .forEach((c) => {
        const li = document.createElement("li");
        const text = document.createElement("div");
        text.textContent = c.text;
        const time = document.createElement("span");
        time.className = "frontier-comment-time";
        time.textContent = c.time;
        li.appendChild(text);
        li.appendChild(time);
        list.appendChild(li);
      });
  }

  function initLike() {
    const btn = document.getElementById("frontier-like-btn");
    const countEl = document.getElementById("frontier-like-count");
    if (!btn || !countEl) return;

    let count = 0;
    try { count = Number(localStorage.getItem(likeKey) || "0"); } catch (_) { /* Storage can be disabled. */ }
    if (!Number.isFinite(count) || count < 0) count = 0;
    countEl.textContent = String(count);

    btn.addEventListener("click", function () {
      count += 1;
      try { localStorage.setItem(likeKey, String(count)); } catch (_) { /* Session-only counter. */ }
      countEl.textContent = String(count);
    });
  }

  function initComments() {
    const form = document.getElementById("frontier-comment-form");
    const input = document.getElementById("frontier-comment-input");
    if (!form || !input) return;

    form.addEventListener("submit", function (e) {
      e.preventDefault();
      const text = (input.value || "").trim();
      if (!text) return;

      const comments = getComments();
      comments.push({
        text: text,
        time: new Date().toLocaleString(),
      });
      if (!saveComments(comments)) {
        alert("浏览器禁止本地存储，留言未保存。请复制保留你的文字。");
        return;
      }
      input.value = "";
      renderComments();
    });

    renderComments();
  }

  function initSmoothAnchor() {
    document
      .querySelectorAll(".frontier-side-toc a[href^='#'], .frontier-inline-toc a[href^='#']")
      .forEach(function (a) {
        a.addEventListener("click", function (e) {
          const id = a.getAttribute("href");
          if (!id) return;
          const target = document.querySelector(id);
          if (!target) return;
          e.preventDefault();
          target.scrollIntoView({ behavior: "smooth", block: "start" });
        });
      });
  }

  document.addEventListener("DOMContentLoaded", function () {
    const search = document.getElementById("frontier-search");
    const topic = document.getElementById("frontier-topic");
    const area = document.getElementById("working-papers");
    if (search && topic && area) {
      const papers = Array.from(area.querySelectorAll("[data-frontier-paper]"));
      const records = papers.map(function (paper) { return { paper: paper, text: paper.textContent.toLocaleLowerCase() }; });
      function filterPapers() {
        const query = search.value.trim().toLocaleLowerCase();
        let count = 0;
        records.forEach(function (record) {
          const show = (topic.value === "all" || record.paper.dataset.topic === topic.value) && (!query || record.text.includes(query));
          record.paper.hidden = !show;
          if (show) count += 1;
        });
        area.querySelectorAll("[data-frontier-topic]").forEach(function (group) {
          group.hidden = !Array.from(group.querySelectorAll("[data-frontier-paper]")).some(function (paper) { return !paper.hidden; });
        });
        document.getElementById("frontier-result-count").textContent = "显示 " + count + " / " + papers.length + " 篇";
        document.getElementById("frontier-no-results").hidden = count !== 0;
      }
      area.querySelector(".frontier-tools").hidden = false;
      search.addEventListener("input", filterPapers);
      topic.addEventListener("change", filterPapers);
      filterPapers();
    }
    if (!document.getElementById("frontier-feedback")) return;
    initLike();
    initComments();
    initSmoothAnchor();
  });
})();
