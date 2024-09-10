document.getElementById('togglePassword').addEventListener('click', function () {
    const passwordInput = document.querySelector('.password-input'); // Seleccionamos el campo con la clase 'password-input'
    const type = passwordInput.getAttribute('type') === 'password' ? 'text' : 'password';
    passwordInput.setAttribute('type', type);

    // Cambiar el ícono del ojo
    this.classList.toggle('fa-eye-slash');
});
