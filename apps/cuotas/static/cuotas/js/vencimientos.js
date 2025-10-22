// =========================================================
//  utilidades
// =========================================================
function $(sel, ctx=document){ return ctx.querySelector(sel); }
function $all(sel, ctx=document){ return Array.from(ctx.querySelectorAll(sel)); }

// =========================================================
//  Tabs
// =========================================================
document.addEventListener('DOMContentLoaded', () => {
  const tabs = $all('.tab-button');
  const panels = $all('.tab-content');
  tabs.forEach(btn=>{
    btn.addEventListener('click', ()=>{
      const target = btn.getAttribute('data-tab');
      tabs.forEach(b=>b.classList.remove('active'));
      panels.forEach(p=>p.classList.remove('active'));
      btn.classList.add('active');
      const pane = document.getElementById(target);
      if(pane) pane.classList.add('active');
    });
  });
});

// =========================================================
//  Filtro rápido de búsqueda
// =========================================================
document.addEventListener('DOMContentLoaded', () => {
  const input = $('#filter-q');
  const table = $('#tabla-vencimientos');
  if(!input || !table) return;

  const rows = $all('tbody tr', table);

  function normalize(s){
    return (s || '').toLowerCase()
      .normalize('NFD')
      .replace(/\p{Diacritic}/gu, '');
  }

  input.addEventListener('input', ()=>{
    const q = normalize(input.value);
    rows.forEach(row=>{
      const text = normalize(row.innerText);
      row.style.display = text.includes(q) ? '' : 'none';
    });
  });

  // Atajo de teclado: presionar "/" para enfocar el filtro
  document.addEventListener('keydown', e=>{
    if(e.key === '/' && document.activeElement !== input){
      e.preventDefault();
      input.focus();
      input.select();
    }
  });
});

// =========================================================
//  Filas clicables (navega a editar)
// =========================================================
document.addEventListener('DOMContentLoaded', () => {
  $all('tr.row-click').forEach(tr=>{
    tr.addEventListener('click', e=>{
      if(e.target.closest('a')) return; // evitar conflicto con enlaces internos
      const url = tr.getAttribute('data-url');
      if(url) window.location.href = url;
    });
  });
});

// =========================================================
//  Exportar a CSV
// =========================================================
document.addEventListener('DOMContentLoaded', () => {
  const btn = $('#btn-export');
  const table = $('#tabla-vencimientos');
  if(!btn || !table) return;

  btn.addEventListener('click', ()=>{
    const rows = $all('tr', table);
    const lines = rows.map((r, idx)=>{
      const cells = $all(idx===0 ? 'th' : 'td', r).map(td=>{
        const text = td.innerText.replace(/\s+/g,' ').trim();
        return text.includes(',') ? `"${text}"` : text;
      });
      return cells.join(',');
    });

    const csv = lines.join('\n');
    const blob = new Blob([csv], {type:'text/csv;charset=utf-8;'});
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    const fecha = new Date().toISOString().slice(0,10);
    a.href = url;
    a.download = `vencimientos_${fecha}.csv`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  });
});
