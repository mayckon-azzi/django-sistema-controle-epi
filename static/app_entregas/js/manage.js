// aprovar/reprovar etc.
document.querySelectorAll('[data-confirm]').forEach((el) => {
  el.addEventListener('click', (e) => {
    const msg = el.getAttribute('data-confirm') || 'Confirmar ação?';
    if (!confirm(msg)) {
      e.preventDefault();
    }
  });
});
