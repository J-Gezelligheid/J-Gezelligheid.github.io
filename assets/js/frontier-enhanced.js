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
    localStorage.setItem(commentsKey, JSON.stringify(comments));
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

    let count = Number(localStorage.getItem(likeKey) || "0");
    if (!Number.isFinite(count) || count < 0) count = 0;
    countEl.textContent = String(count);

    btn.addEventListener("click", function () {
      count += 1;
      localStorage.setItem(likeKey, String(count));
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
      saveComments(comments);
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
    if (!document.getElementById("frontier-feedback")) return;
    initLike();
    initComments();
    initSmoothAnchor();
  });
})();
