(function () {
  function initSmoothAnchor() {
    document
      .querySelectorAll(".drug-watch-side-toc a[href^='#'], .drug-watch-inline-toc a[href^='#']")
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
    if (!document.querySelector(".drug-watch-inline-toc, .drug-watch-side-toc")) return;
    initSmoothAnchor();
  });
})();
