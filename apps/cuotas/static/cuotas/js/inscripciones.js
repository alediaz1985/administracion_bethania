// Filas clicables
document.querySelectorAll('tr[data-url]')?.forEach(tr => {
  tr.addEventListener('click', (e) => {
    if (e.target.closest('.actions')) return;
    const url = tr.getAttribute('data-url');
    if (url) window.location.href = url;
  });
});