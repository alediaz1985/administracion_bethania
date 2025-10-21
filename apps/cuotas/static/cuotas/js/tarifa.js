// static/cuotas/js/tarifa.js

(function(){
  const form = document.getElementById('tarifa-form');
  const btnGuardar = document.getElementById('btn-guardar');

  // Previene doble submit
  if (form && btnGuardar) {
    form.addEventListener('submit', function(e){
      // Si la validación front falla, no deshabilitamos
      if (!form.checkValidity()) {
        e.preventDefault();
        e.stopPropagation();
        marcarErrores(form);
        return false;
      }
      btnGuardar.disabled = true;
      btnGuardar.textContent = 'Guardando...';
    });
  }

  // Atajo: Ctrl+S para enviar
  document.addEventListener('keydown', function(e){
    if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === 's') {
      e.preventDefault();
      if (form) form.requestSubmit();
    }
  });

  // Validación suave y marcado de errores
  function marcarErrores(f){
    f.classList.add('was-validated');
    const requiredFields = f.querySelectorAll('[required]');
    requiredFields.forEach(el=>{
      if (!el.value) {
        el.classList.add('is-invalid');
      } else {
        el.classList.remove('is-invalid');
      }
    });
  }

  // Formato soft para montos (2 decimales al salir del input)
  const moneyInputs = document.querySelectorAll('input[name="monto_inscripcion"], input[name="monto_cuota_mensual"]');
  moneyInputs.forEach(inp=>{
    // Asegura step/validación nativa
    inp.setAttribute('step', '0.01');
    inp.setAttribute('min', '0');

    inp.addEventListener('blur', ()=>{
      const val = inp.value.replace(',', '.').trim();
      if (val === '') return;
      const num = Number(val);
      if (!Number.isNaN(num)) {
        inp.value = num.toFixed(2);
        inp.classList.remove('is-invalid');
      } else {
        inp.classList.add('is-invalid');
      }
    });
  });
})();
