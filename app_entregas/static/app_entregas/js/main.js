function filterSelect(selectId, query) {
  const sel = document.getElementById(selectId);
  if (!sel) return;
  const norm = s => s
    .toString()
    .normalize("NFD")
    .replace(/\p{Diacritic}/gu, "")
    .toLowerCase();
  const q = norm(query || "");
  let visible = 0;
  for (const opt of sel.options) {
    const text = norm(opt.textContent + " " + opt.value);
    const hit = !q || text.includes(q);
    opt.hidden = !hit;
    if (hit) visible++;
  }
  // Se apenas 1 opção permanecer visível, seleciona automaticamente
  if (visible === 1) {
    const only = [...sel.options].find(o => !o.hidden);
    if (only) sel.value = only.value;
  }
}
