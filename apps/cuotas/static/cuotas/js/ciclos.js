// Tabs
const tabs = document.querySelectorAll('.tab-button');
const panels = document.querySelectorAll('.tab-content');

tabs.forEach(btn=>{
  btn.addEventListener('click', ()=>{
    const target = btn.getAttribute('data-tab');
    tabs.forEach(b=>b.classList.remove('active'));
    panels.forEach(p=>p.classList.remove('active'));
    btn.classList.add('active');
    document.getElementById(target).classList.add('active');
    // Accesibilidad
    tabs.forEach(b=>b.setAttribute('aria-selected', b===btn ? 'true':'false'));
    panels.forEach(p=>p.setAttribute('aria-hidden', p.id===target ? 'false':'true'));
    // Scroll suave al inicio de la tarjeta
    document.querySelector('.student-card')?.scrollIntoView({ behavior:'smooth', block:'start' });
  });
});

// Jump links (botones de la cabecera)
document.querySelectorAll('[data-jump]').forEach(a=>{
  a.addEventListener('click', (e)=>{
    e.preventDefault();
    const id = a.getAttribute('data-jump');
    const btn = document.querySelector(`.tab-button[data-tab="${id}"]`);
    btn?.click();
  });
});

// Atajos de teclado: N = nuevo, L = listado, S = submit crear
document.addEventListener('keydown', (e)=>{
  const tag = (document.activeElement?.tagName || '').toUpperCase();
  const typing = ['INPUT','TEXTAREA','SELECT'].includes(tag);
  if (typing) return;

  const clickTab = (id)=>{
    document.querySelector(`.tab-button[data-tab="${id}"]`)?.click();
  };

  switch(e.key.toLowerCase()){
    case 'n': clickTab('tab-crear'); break;
    case 'l': clickTab('tab-listado'); break;
    case 's':
      const createVisible = document.getElementById('tab-crear')?.classList.contains('active');
      if (createVisible) document.getElementById('form-crear-ciclo')?.requestSubmit();
      break;
  }
});
