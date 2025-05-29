lucide.createIcons();
AOS.init();

const dataNiveles = {
    labels: nivelesLabels,
    datasets: [{
        label: 'Estudiantes por nivel',
        data: nivelesData,
        backgroundColor: ['#3498db', '#2ecc71', '#e74c3c', '#9b59b6'],
    }]
};

const configNiveles = {
    type: 'doughnut',
    data: dataNiveles,
    options: {
        responsive: true,
        plugins: {
            legend: {
                position: 'bottom'
            }
        }
    }
};

new Chart(document.getElementById('graficoNiveles'), configNiveles);

// Segundo gráfico: Pagos por curso
const dataPagos = {
    labels: cursosLabels,
    datasets: [
        {
            label: 'En término',
            data: pagosEnTermino,
            backgroundColor: '#2ecc71'
        },
        {
            label: 'Fuera de término',
            data: pagosFueraDeTermino,
            backgroundColor: '#e74c3c'
        }
    ]
};

const configPagos = {
    type: 'bar',
    data: dataPagos,
    options: {
        responsive: true,
        plugins: {
            legend: {
                position: 'top'
            }
        },
        scales: {
            x: {
                stacked: true
            },
            y: {
                stacked: true,
                beginAtZero: true
            }
        }
    }
};

new Chart(document.getElementById('graficoPagos'), configPagos);
