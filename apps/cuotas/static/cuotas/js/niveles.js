// Niveles – JS liviano y desacoplado
(function () {
  const tabla = document.getElementById('tabla-niveles');
  if (!tabla) return;

  const btnNuevo = document.getElementById('btn-nuevo');
  const inputQ  = document.getElementById('q');

  // Atajo: N => Nuevo Nivel (si no estás tipeando en inputs)
  document.addEventListener('keydown', function (e) {
    if (!btnNuevo) return;
    const tag = (e.target.tagName || '').toLowerCase();
    if (tag === 'input' || tag === 'textarea' || e.ctrlKey || e.metaKey || e.altKey) return;
    if ((e.key || '').toLowerCase() === 'n') {
      window.location.href = btnNuevo.getAttribute('href');
    }
  });

  // Foco si hay query y resaltado simple
  const params = new URLSearchParams(window.location.search);
  const q = (params.get('q') || '').trim();

  if (q && inputQ) {
    try {
      inputQ.focus();
      inputQ.setSelectionRange(inputQ.value.length, inputQ.value.length);
    } catch (_) {}
  }

  if (q) {
    const needle = q.toLowerCase();
    const celdas = tabla.querySelectorAll('.nombre-nivel');
    celdas.forEach(td => {
      const raw = td.textContent || '';
      const idx = raw.toLowerCase().indexOf(needle);
      if (idx >= 0) {
        td.innerHTML =
          raw.slice(0, idx) +
          '<mark>' + raw.slice(idx, idx + q.length) + '</mark>' +
          raw.slice(idx + q.length);
      }
    });
  }
})();
