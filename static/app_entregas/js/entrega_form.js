(function () {
  function byId(id) { return document.getElementById(id); }

  function toggleBlocks() {
    const statusEl = document.getElementById("id_status");
    if (!statusEl) return;

    const val = statusEl.value || "";

    const showPrevista = (val === "EMPRESTADO" || val === "EM_USO");
    const showDevolucao = (val === "DEVOLVIDO" || val === "DANIFICADO" || val === "PERDIDO");

    const prev = byId("wrap_prevista");
    const dev = byId("wrap_devolucao");
    const obsDev = byId("wrap_obs_devolucao");

    if (prev) prev.classList.toggle("d-none", !showPrevista);
    if (dev) dev.classList.toggle("d-none", !showDevolucao);
    if (obsDev) obsDev.classList.toggle("d-none", !showDevolucao);
  }

  document.addEventListener("change", function (ev) {
    if (ev.target && ev.target.id === "id_status") {
      toggleBlocks();
    }
  });

  document.addEventListener("DOMContentLoaded", toggleBlocks);
})();
