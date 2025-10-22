// Click en fila para entrar a editar
(document.querySelectorAll('tr[data-url]') || []).forEach(tr => {
  tr.addEventListener('click', (e) => {
    if (e.target.closest('.actions')) return; // no disparar si apretó en acciones
    const url = tr.getAttribute('data-url');
    if (url) window.location.href = url;
  });
});

// Aviso básico si intenta enviar porcentaje>100 o <0 (defensa extra UX)
const porcentaje = document.querySelector('#id_porcentaje');
if (porcentaje) {
  porcentaje.addEventListener('change', () => {
    const v = parseFloat(porcentaje.value);
    if (!isNaN(v) && (v < 0 || v > 100)) {
      alert('El porcentaje debe estar entre 0 y 100.');
      porcentaje.focus();
    }
  });
}

// En formularios, si ambos campos están vacíos o 0, alert (UX)
const form = document.querySelector('form');
if (form) {
  form.addEventListener('submit', (e) => {
    const p = document.querySelector('#id_porcentaje');
    const m = document.querySelector('#id_monto_fijo');
    const pv = p ? parseFloat(p.value || '0') : 0;
    const mv = m ? parseFloat(m.value || '0') : 0;
    if ((isNaN(pv) || pv <= 0) && (isNaN(mv) || mv <= 0)) {
      const ok = confirm('No ingresaste porcentaje ni monto fijo (>0). ¿Deseás continuar?');
      if (!ok) e.preventDefault();
    }
  });
}