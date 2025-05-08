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

function toggleSidebar() {
    const sidebar = document.getElementById("sidebar");
    const content = document.querySelector(".open-btn");

    // Alterna la clase 'active'
    sidebar.classList.toggle("active");

    // Ocultar o mostrar iconos
    if (sidebar.classList.contains("active")) {
        content.style.marginLeft = "0.5%";
        sidebar.classList.remove("no-icons");
    } else {
        content.style.marginLeft = "0px";
        sidebar.classList.add("no-icons");
    }

    // ✅ Mover el botón al 20% o 4% según el estado
    content.style.left = sidebar.classList.contains("active") ? "15%" : "4%";
}

document.addEventListener('click', function (e) {
    const sidebar = document.getElementById("sidebar");
    const content = document.querySelector(".open-btn"); // El botón de abrir la barra
    const isClickInside = sidebar.contains(e.target);
    const isToggleButton = e.target.closest('.open-btn'); // Comprobamos si el clic fue en el botón

    // Si el clic fue fuera de la barra y el botón
    if (!isClickInside && !isToggleButton && sidebar.classList.contains("active")) {
        sidebar.classList.remove("active");

        // Restablecemos la posición del botón al cerrarse la barra
        content.style.marginLeft = "0px";
        content.style.left = "4%"; // Volvemos al estado inicial (barra cerrada)
    }
});

// Función para expandir los subitems de un ítem específico
const expandBtns = document.querySelectorAll('.sidebar-items > li > a');

expandBtns.forEach(btn => {
    btn.addEventListener('click', function(e) {
        e.preventDefault();  // Prevenir la acción predeterminada del enlace

        const sidebar = document.getElementById("sidebar");

        // No hacer nada si la barra lateral está cerrada
        if (!sidebar.classList.contains('active')) {
            return;
        }

        const subitems = this.nextElementSibling;  // Los subitems del ítem clickeado

        // Verificar si ya está abierto
        const isActive = subitems.classList.contains('active');
        
        // Si el subitem ya está abierto, lo cerramos
        if (isActive) {
            subitems.classList.remove('active');
            this.querySelector('.expand-btn').textContent = '+';  // Cambiar icono a '+'
        } else {
            // Si no está abierto, cerramos todos los subitems primero
            document.querySelectorAll('.subitems').forEach(sub => {
                sub.classList.remove('active');
                sub.previousElementSibling.querySelector('.expand-btn').textContent = '+';  // Revertir todos los iconos a '+'
            });

            // Abrimos el subitem del ítem seleccionado
            subitems.classList.add('active');
            this.querySelector('.expand-btn').textContent = '-';  // Cambiar icono a '-'
        }
    });
});
// Cierra la sidebar si se hace clic fuera de ella
document.addEventListener('click', function (e) {
    const sidebar = document.getElementById("sidebar");
    const isClickInside = sidebar.contains(e.target);
    const isToggleButton = e.target.closest('.open-btn'); // botón que abre la sidebar

    if (!isClickInside && !isToggleButton && sidebar.classList.contains("active")) {
        sidebar.classList.remove("active");

        const content = document.querySelector(".open-btn");
        content.style.marginLeft = "0px";
    }
});

const yearSpan = document.getElementById("anio-actual");
yearSpan.textContent = new Date().getFullYear();