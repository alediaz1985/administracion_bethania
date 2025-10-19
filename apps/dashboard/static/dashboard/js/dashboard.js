// apps/dashboard/static/dashboard/js/dashboard.js

(function () {
  // Esperar al DOM + a que las libs externas hayan cargado (defer en HTML)
  document.addEventListener('DOMContentLoaded', function () {
    // --- Iconos y animaciones ---
    if (window.lucide && typeof window.lucide.createIcons === 'function') {
      window.lucide.createIcons();
    }
    if (window.AOS && typeof window.AOS.init === 'function') {
      window.AOS.init({ duration: 600, once: true });
    }

    // --- Helper: lee JSON seguro del template (json_script) ---
    function readJSON(id) {
      const el = document.getElementById(id);
      if (!el) return [];
      try { return JSON.parse(el.textContent); }
      catch { return []; }
    }

    // Datos
    const nivelesLabels  = readJSON('niveles-labels');
    const nivelesData    = readJSON('niveles-data');
    const turnosLabels   = readJSON('turnos-labels');
    const turnosData     = readJSON('turnos-data');
    const ciudadesLabels = readJSON('ciudades-labels');
    const ciudadesData   = readJSON('ciudades-data');

    // Si no está Chart.js, salimos silenciosamente
    if (!window.Chart) return;

    // Colores desde CSS
    const cs = getComputedStyle(document.documentElement);
    const getVar = (name) => cs.getPropertyValue(name).trim();
    const chartColors = [
      getVar('--chart-1'), getVar('--chart-2'), getVar('--chart-3'), getVar('--chart-4'),
      getVar('--chart-5'), getVar('--chart-6'), getVar('--chart-7'), getVar('--chart-8'),
    ];
    const text2  = getVar('--text-2');
    const bg1    = getVar('--bg-1');
    const bg3    = getVar('--bg-3');
    const border = getVar('--border');

    // Opciones comunes
    const commonOptions = {
      responsive: true,
      maintainAspectRatio: false, // el contenedor .chart-canvas define la altura
      layout: { padding: 8 },
      plugins: {
        legend: {
          position: 'bottom',
          labels: {
            color: text2,
            font: { family: 'Inter', size: 12, weight: 500 },
            usePointStyle: true,
            boxWidth: 8
          }
        },
        tooltip: {
          backgroundColor: bg3,
          borderColor: border,
          borderWidth: 1,
          titleFont: { family: 'Inter', weight: '600' },
          bodyFont: { family: 'Inter', size: 12 },
          padding: 10,
          displayColors: false
        }
      }
    };

    // --- Chart 1: Donut niveles ---
    const elNiveles = document.getElementById('chartNiveles');
    if (elNiveles) {
      new Chart(elNiveles, {
        type: 'doughnut',
        data: {
          labels: nivelesLabels,
          datasets: [{
            label: 'Estudiantes',
            data: nivelesData,
            backgroundColor: chartColors.slice(0, nivelesData.length),
            borderColor: bg1,
            borderWidth: 2,
            hoverOffset: 10
          }]
        },
        options: { ...commonOptions, cutout: '65%' }
      });
    }

    // --- Chart 2: Barras turnos ---
    const elTurnos = document.getElementById('chartTurnos');
    if (elTurnos) {
      new Chart(elTurnos, {
        type: 'bar',
        data: {
          labels: turnosLabels,
          datasets: [{
            label: 'Turnos',
            data: turnosData,
            backgroundColor: chartColors.slice(0, turnosData.length),
            borderRadius: 6
          }]
        },
        options: {
          ...commonOptions,
          scales: {
            x: {
              ticks: { color: text2, font: { family: 'Inter' } },
              grid: { color: border }
            },
            y: {
              beginAtZero: true,
              ticks: { color: text2, stepSize: 1 },
              grid: { color: border }
            }
          }
        }
      });
    }

    // --- Chart 3: Barras ciudades ---
    const elCiudades = document.getElementById('chartCiudades');
    if (elCiudades) {
      new Chart(elCiudades, {
        type: 'bar',
        data: {
          labels: ciudadesLabels,
          datasets: [{
            label: 'Estudiantes',
            data: ciudadesData,
            backgroundColor: chartColors.slice(0, ciudadesData.length),
            borderRadius: 6
          }]
        },
        options: {
          ...commonOptions,
          scales: {
            x: {
              ticks: { color: text2, font: { family: 'Inter' } },
              grid: { color: border }
            },
            y: {
              beginAtZero: true,
              ticks: { color: text2, stepSize: 1 },
              grid: { color: border }
            }
          }
        }
      });
    }
  });
})();
