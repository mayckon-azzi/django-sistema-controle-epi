
window.toggleSidebar = function () {
  document.body.classList.toggle("sidebar-open");
};

document.addEventListener("click", function (e) {
  if (document.body.classList.contains("sidebar-open")) {
    const sidebar = document.querySelector(".sidebar");
    const topbar = document.querySelector(".topbar");
    if (!sidebar.contains(e.target) && !topbar.contains(e.target)) {
      document.body.classList.remove("sidebar-open");
    }
  }
});

// ===== Sidebar colapsável (desktop) com persistência =====
(function initSidebarCollapse() {
  try {
    const saved = localStorage.getItem("sidebarCollapsed");
    if (saved === "1") {
      document.body.classList.add("sidebar-collapsed");
      const btn = document.querySelector(".collapse-btn");
      if (btn) btn.setAttribute("aria-expanded", "false");
    }
  } catch (_) {}
})();

window.toggleSidebarCollapse = function () {
  document.body.classList.toggle("sidebar-collapsed");
  const collapsed = document.body.classList.contains("sidebar-collapsed");
  try { localStorage.setItem("sidebarCollapsed", collapsed ? "1" : "0"); } catch (_) {}
  const btn = document.querySelector(".collapse-btn");
  if (btn) btn.setAttribute("aria-expanded", collapsed ? "false" : "true");
};

// ===== Ativo acessível (garante aria-current na rota ativa) =====
(function markActive() {
  const links = document.querySelectorAll(".sidenav .item");
  if (!links.length) return;
  // URL atual (sem querystring/hash)
  const here = location.pathname.replace(/\/+$/, "") || "/";
  let marked = false;
  links.forEach(a => {
    const href = (a.getAttribute("href") || "").replace(/\/+$/, "") || "/";
    if (here === href || (here.startsWith(href + "/") && href !== "/")) {
      a.setAttribute("aria-current", "page");
      marked = true;
    }
  });
  // fallback: se nenhum marcado, marca o primeiro com .active (renderizado pelo Django)
  if (!marked) {
    const active = document.querySelector(".sidenav .item.active");
    if (active) active.setAttribute("aria-current", "page");
  }
})();
