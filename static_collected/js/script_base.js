document.addEventListener('DOMContentLoaded', function() {
    const menuItems = document.querySelectorAll('.menu-item');

    menuItems.forEach(item => {
        item.addEventListener('mouseenter', () => {
            const submenu = item.querySelector('.submenu');
            if (submenu) {
                submenu.style.display = 'block';
                submenu.style.opacity = '1';
                submenu.style.transform = 'translateY(0)';
            }
        });

        item.addEventListener('mouseleave', () => {
            const submenu = item.querySelector('.submenu');
            if (submenu) {
                submenu.style.opacity = '0';
                submenu.style.transform = 'translateY(-20px)';
                setTimeout(() => {
                    submenu.style.display = 'none';
                }, 300); // Esperar a que la transición termine antes de ocultarlo
            }
        });
    });
});
