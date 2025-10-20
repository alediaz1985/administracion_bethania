// Tarjetas clicables (usa el data-url del <article>)
document.querySelectorAll('.feature-card[data-url]').forEach(card => {
  card.addEventListener('click', (e) => {
    // Evitar que un click en <a> dentro dispare doble navegación
    if (e.target.tagName.toLowerCase() !== 'a') {
      const url = card.getAttribute('data-url');
      if (url) window.location.href = url;
    }
  });
});

// Tabs simples
const tabs = document.querySelectorAll('.tab-button');
const panels = document.querySelectorAll('.tab-content');
tabs.forEach(btn=>{
  btn.addEventListener('click', ()=>{
    const target = btn.getAttribute('data-tab');
    tabs.forEach(b=>b.classList.remove('active'));
    panels.forEach(p=>p.classList.remove('active'));
    btn.classList.add('active');
    document.getElementById(target).classList.add('active');
  });
});

// Atajos de teclado (navegación rápida)
document.addEventListener('keydown', (e)=>{
  if (['INPUT','TEXTAREA','SELECT'].includes((document.activeElement.tagName||'').toUpperCase())) return;
  const go = (url)=> url && (window.location.href = url);

  switch(e.key.toLowerCase()){
    case 'i': go(document.querySelector("[href$='inscripcion_list/']")?.href); break;
    case 'n': go(document.querySelector("[href$='inscripcion_create/']")?.href); break;
    case 'c': go(document.querySelector("[href$='ciclo_list/']")?.href); break;
    case 'l': go(document.querySelector("[href$='inscripcion_list/']")?.href); break;
    case 'r': go(document.querySelector("[href$='curso_list/']")?.href); break;
    case 't': go(document.querySelector("[href$='tarifa_list/']")?.href); break;
    case 'v': go(document.querySelector("[href$='vencimiento_list/']")?.href); break;
    case 'b': go(document.querySelector("[href$='beneficio_list/']")?.href); break;
    case 'a': go(document.querySelector("[href$='beneficio_insc_list/']")?.href); break;
  }
});
