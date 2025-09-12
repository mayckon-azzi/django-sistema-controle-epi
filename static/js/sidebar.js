(function () {
  const sidebar = document.getElementById('app-sidebar');

  // Em telas pequenas, o hover não é viável — então usamos "toque" para expandir temporariamente
  const prefersHover = window.matchMedia('(hover: hover)').matches;

  if (!prefersHover && sidebar) {
    let timer;
    const open = () => sidebar.classList.add('expanded');
    const close = () => sidebar.classList.remove('expanded');

    sidebar.addEventListener('touchstart', () => {
      open();
      clearTimeout(timer);
      timer = setTimeout(close, 3000);
    });
  }
})();