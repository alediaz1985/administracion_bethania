// apps/cuotas/static/cuotas/js/home.js
document.addEventListener("DOMContentLoaded", () => {
  // ================================
  // Feature-cards clicables
  // ================================
  const cards = document.querySelectorAll(".feature-card[data-url]");
  cards.forEach(card => {
    card.style.cursor = "pointer";
    card.setAttribute("tabindex", "0");            // accesible con teclado
    card.setAttribute("role", "link");
    card.addEventListener("click", (e) => {
      // Si clickean un <a> o un control interactivo adentro, no duplicar navegación
      if (e.target.closest("a, button, input, select, textarea, label")) return;

      const url = card.getAttribute("data-url");
      if (!url) return;

      // Click medio → nueva pestaña
      if (e.button === 1) {
        window.open(url, "_blank");
        return;
      }

      // Ctrl/Cmd + click → nueva pestaña
      if (e.ctrlKey || e.metaKey) {
        window.open(url, "_blank");
        return;
      }

      // Navegación normal
      window.location.href = url;
    });

    // Teclado: Enter o Space activan la tarjeta
    card.addEventListener("keydown", (e) => {
      if (e.key === "Enter" || e.key === " ") {
        e.preventDefault();
        const url = card.getAttribute("data-url");
        if (url) window.location.href = url;
      }
    });
  });

  // ================================
  // Tabs accesibles + persistencia
  // ================================
  const tabButtons = document.querySelectorAll(".tabs .tab-button");
  const tabPanels  = document.querySelectorAll(".tab-content");

  function activateTab(targetId, btn) {
    tabPanels.forEach(panel => {
      const isActive = panel.id === targetId;
      panel.classList.toggle("active", isActive);
      panel.setAttribute("aria-hidden", String(!isActive));
    });

    tabButtons.forEach(b => {
      const isSelected = b === btn;
      b.classList.toggle("active", isSelected);
      b.setAttribute("aria-selected", String(isSelected));
    });

    // Actualiza hash para permitir “deep link”
    if (targetId) {
      history.replaceState(null, "", `#${targetId}`);
      // Persistir pestaña (opcional)
      try { localStorage.setItem("cuotas_home_active_tab", targetId); } catch(_) {}
    }
  }

  tabButtons.forEach(btn => {
    btn.setAttribute("role", "tab");
    btn.addEventListener("click", (e) => {
      e.preventDefault();
      const targetId = btn.dataset.tab;
      if (!targetId) return;
      activateTab(targetId, btn);
    });
  });

  // Activación inicial: hash > localStorage > primera
  (function initTabs() {
    const byHash = location.hash && location.hash.slice(1);
    const byLS   = (() => { try { return localStorage.getItem("cuotas_home_active_tab"); } catch(_) { return null; }})();
    const target = byHash || byLS || (tabButtons[0]?.dataset.tab);
    const btn    = [...tabButtons].find(b => b.dataset.tab === target) || tabButtons[0];
    if (btn) activateTab(btn.dataset.tab, btn);
  })();

  // ================================
  // Atajos de teclado (navegación)
  // ================================
  document.addEventListener("keydown", (e) => {
    // Evitar en inputs
    const tag = (document.activeElement?.tagName || "").toUpperCase();
    if (["INPUT", "TEXTAREA", "SELECT"].includes(tag) || e.altKey || e.ctrlKey || e.metaKey) return;

    // Primero probá buscar por data-shortcut="i|n|c|l|r|t|v|b|a"
    const go = (selector) => {
      const el = document.querySelector(selector);
      const href = el?.getAttribute("href");
      if (href) {
        window.location.href = href;
        return true;
      }
      return false;
    };

    switch (e.key.toLowerCase()) {
      case "i": if (go('[data-shortcut="i"]')) return; break; // inscripcion_list
      case "n": if (go('[data-shortcut="n"]')) return; break; // inscripcion_create
      case "c": if (go('[data-shortcut="c"]')) return; break; // ciclo_list
      case "l": if (go('[data-shortcut="l"]')) return; break; // inscripcion_list (alias)
      case "r": if (go('[data-shortcut="r"]')) return; break; // curso_list
      case "t": if (go('[data-shortcut="t"]')) return; break; // tarifa_list
      case "v": if (go('[data-shortcut="v"]')) return; break; // vencimiento_list
      case "b": if (go('[data-shortcut="b"]')) return; break; // beneficio_list
      case "a": if (go('[data-shortcut="a"]')) return; break; // beneficio_insc_list
      default: return;
    }

    // Fallback (por si aún no añadiste data-shortcut): busca por sufijos de URL
    const suffix = {
      i: "inscripcion_list/",
      n: "inscripcion_create/",
      c: "ciclo_list/",
      l: "inscripcion_list/",
      r: "curso_list/",
      t: "tarifa_list/",
      v: "vencimiento_list/",
      b: "beneficio_list/",
      a: "beneficio_insc_list/"
    }[e.key.toLowerCase()];

    if (suffix) {
      const link = document.querySelector(`a[href$='${suffix}']`);
      if (link?.href) {
        window.location.href = link.href;
      }
    }
  });
});
