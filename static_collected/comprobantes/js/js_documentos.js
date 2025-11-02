/* =====================================================
   Documentos — JS
===================================================== */

function initTooltips() {
  var els = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
  els.forEach(function (el) {
    // eslint-disable-next-line no-undef
    new bootstrap.Tooltip(el);
  });
}

function preventDoubleSubmit() {
  document.querySelectorAll('.doc-confirm-form').forEach(function (form) {
    form.addEventListener('submit', function (e) {
      var btn = form.querySelector('button[type="submit"]');
      if (!btn) return;
      if (btn.dataset.locked === '1') { e.preventDefault(); return false; }
      btn.dataset.locked = '1';
      btn.classList.add('disabled');
      btn.setAttribute('aria-disabled', 'true');
      btn.innerHTML = '<span class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>Procesando…';
    });
  });
}

function spinnerOnOpenDownload() {
  var btn = document.querySelector('[data-bs-target="#modalDescargar"]');
  if (!btn) return;
  btn.addEventListener('click', function(){
    var sp = btn.querySelector('.spinner-border');
    if (sp) sp.classList.remove('d-none');
    var modal = document.querySelector('#modalDescargar');
    if (modal) {
      modal.addEventListener('hidden.bs.modal', function(){
        if (sp) sp.classList.add('d-none');
      }, { once:true });
    }
  });
}

document.addEventListener('DOMContentLoaded', function(){
  initTooltips();
  preventDoubleSubmit();
  spinnerOnOpenDownload();
});
