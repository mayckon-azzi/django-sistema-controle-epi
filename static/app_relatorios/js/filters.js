
(function () {
  const form = document.getElementById('reportFilters');
  if (!form) return;

  form.querySelectorAll('select').forEach((el) => {
    el.addEventListener('change', () => form.submit());
  });
})();