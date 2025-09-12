// Fecha outros submenus ao abrir um (acordeão simples)
document.addEventListener('DOMContentLoaded', () => {
  const sidebar = document.getElementById('sidebar');
  if (!sidebar) return;

  sidebar.addEventListener('show.bs.collapse', (e) => {
    const opened = sidebar.querySelectorAll('.collapse.show');
    opened.forEach(el => {
      if (el !== e.target) {
        const inst = bootstrap.Collapse.getOrCreateInstance(el);
        inst.hide();
      }
    });
  });

  // Evita "cliques" acidentais quando ainda colapsado (só ícones):
  // se a sidebar estiver colapsada (largura pequena), ao primeiro clique no botão do menu, só expande (via hover) sem abrir submenu
  sidebar.querySelectorAll('.btn-toggle').forEach(btn => {
    btn.addEventListener('click', (ev) => {
      const isCollapsed = sidebar.offsetWidth < 100;
      if (isCollapsed) {
        // força um "hover" programático rápido: desloca foco pro sidebar
        sidebar.classList.add('hovering');
        setTimeout(() => sidebar.classList.remove('hovering'), 300);
        ev.preventDefault();
      }
    });
  });
});
