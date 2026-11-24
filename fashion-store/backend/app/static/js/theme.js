(function () {
  var KEY = "swaga-theme";
  var root = document.documentElement;

  function current() {
    return root.getAttribute("data-theme") || "system";
  }

  function apply(mode) {
    if (!["light", "dark", "system"].includes(mode)) mode = "system";
    root.setAttribute("data-theme", mode);
    try {
      localStorage.setItem(KEY, mode);
    } catch (e) {}
    document.querySelectorAll("[data-theme-btn]").forEach(function (btn) {
      btn.setAttribute("aria-pressed", btn.getAttribute("data-theme-btn") === mode ? "true" : "false");
    });
  }

  document.addEventListener("DOMContentLoaded", function () {
    apply(current());
    document.querySelectorAll("[data-theme-btn]").forEach(function (btn) {
      btn.addEventListener("click", function () {
        apply(btn.getAttribute("data-theme-btn"));
      });
    });
  });

  window.matchMedia("(prefers-color-scheme: dark)").addEventListener("change", function () {
    if (current() === "system") apply("system");
  });
})();
