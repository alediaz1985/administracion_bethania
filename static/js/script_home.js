// Se asegura de que solo afecte este bloque específico
const blockHeroContainer = document.querySelector('.block-content-hero .carousel');
const blockCircles = document.querySelectorAll('.block-content-hero .circle');
const blockBlurredBackground = document.querySelector('.block-content-hero .blurred-background');
let blockCurrentImageIndex = 0;
const blockImages = [
    'static/img/colegio.jpg',
    'static/img/colegio2.jpg',
    'static/img/colegio3.jpg'
];

// Cambiar imagen en el carrusel
function blockUpdateCarousel(index) {
    // Cambiar el fondo difuminado
    blockBlurredBackground.style.backgroundImage = `url(${blockImages[index]})`;
    
    // Cambiar imagen en el carrusel
    blockHeroContainer.style.transform = `translateX(-${index * 100 / blockImages.length}%)`;
    
    blockCurrentImageIndex = index;
    blockUpdateCircles();
}

// Actualiza los círculos de control
function blockUpdateCircles() {
    blockCircles.forEach((circle, idx) => {
        if (idx === blockCurrentImageIndex) {
            circle.classList.add('active');
        } else {
            circle.classList.remove('active');
        }
    });
}

// Cambio automático de imagen cada 5 segundos
setInterval(() => {
    blockCurrentImageIndex = (blockCurrentImageIndex + 1) % blockImages.length;
    blockUpdateCarousel(blockCurrentImageIndex);
}, 5000);

// Cambia la imagen al hacer clic en los círculos
blockCircles.forEach((circle, idx) => {
    circle.addEventListener('click', () => {
        blockUpdateCarousel(idx);
    });
});

// Inicializar con la primera imagen
blockUpdateCarousel(blockCurrentImageIndex);
