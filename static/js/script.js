/**
 * CarbonTrack - Client-Side JavaScript
 * Handles Chart.js rendering, number counter animation,
 * interactive form toggles, input validation, and modal confirmation.
 */

document.addEventListener('DOMContentLoaded', () => {
  initMobileNav();
  initWaterModeToggle();
  initCountUpAnimations();
  initCategoryToggles();
  initFormValidation();
  initModalConfirmations();
});

/* -------------------------------------------------------------------------- */
/* 1. Category Selection & Dynamic Toggles                                   */
/* -------------------------------------------------------------------------- */
function setCategoryActive(catName, isActive) {
  const card = document.getElementById(`sec-${catName}`);
  const headerCheckbox = document.getElementById(`toggle-${catName}`);
  const pill = document.querySelector(`.category-pill[data-category="${catName}"]`);
  const hiddenInput = document.getElementById(`include-input-${catName}`);

  if (headerCheckbox) headerCheckbox.checked = isActive;
  if (hiddenInput) hiddenInput.value = isActive ? 'yes' : 'no';

  if (pill) {
    if (isActive) {
      pill.classList.add('active');
    } else {
      pill.classList.remove('active');
    }
    const pillCheck = pill.querySelector('input[type="checkbox"]');
    if (pillCheck) pillCheck.checked = isActive;
  }

  if (card) {
    if (isActive) {
      card.classList.remove('is-disabled');
    } else {
      card.classList.add('is-disabled');
    }
  }
}

function initCategoryToggles() {
  const categories = ['transportation', 'electricity', 'lpg', 'food', 'waste', 'water'];

  // Handle Category Pills in Toolbar
  const pills = document.querySelectorAll('.category-pill');
  pills.forEach(pill => {
    pill.addEventListener('click', (e) => {
      // Avoid duplicate click event if clicking direct checkbox
      if (e.target.tagName !== 'INPUT') {
        const cat = pill.getAttribute('data-category');
        const isNowActive = !pill.classList.contains('active');
        setCategoryActive(cat, isNowActive);
      }
    });

    const pillInput = pill.querySelector('input[type="checkbox"]');
    if (pillInput) {
      pillInput.addEventListener('change', (e) => {
        const cat = pill.getAttribute('data-category');
        setCategoryActive(cat, e.target.checked);
      });
    }
  });

  // Handle Section Card Header Checkboxes
  categories.forEach(cat => {
    const toggle = document.getElementById(`toggle-${cat}`);
    if (toggle) {
      toggle.addEventListener('change', (e) => {
        setCategoryActive(cat, e.target.checked);
      });
    }
  });

  // Quick Select Action Buttons
  const selectAllBtn = document.getElementById('btn-select-all');
  if (selectAllBtn) {
    selectAllBtn.addEventListener('click', () => {
      categories.forEach(cat => setCategoryActive(cat, true));
    });
  }

  const clearAllBtn = document.getElementById('btn-clear-all');
  if (clearAllBtn) {
    clearAllBtn.addEventListener('click', () => {
      categories.forEach(cat => setCategoryActive(cat, false));
    });
  }
}

/* -------------------------------------------------------------------------- */
/* 1. Mobile Navigation Toggle                                                */
/* -------------------------------------------------------------------------- */
function initMobileNav() {
  const toggleBtn = document.querySelector('.nav-toggle');
  const navMenu = document.querySelector('.nav-menu');

  if (toggleBtn && navMenu) {
    toggleBtn.addEventListener('click', () => {
      navMenu.classList.toggle('open');
    });
  }
}

/* -------------------------------------------------------------------------- */
/* 2. Water Calculation Mode Toggle (Direct Liters vs Household Size)         */
/* -------------------------------------------------------------------------- */
function initWaterModeToggle() {
  const modeRadios = document.querySelectorAll('input[name="water_entry_mode"]');
  const directContainer = document.getElementById('water-direct-container');
  const estimateContainer = document.getElementById('water-estimate-container');

  if (modeRadios.length > 0 && directContainer && estimateContainer) {
    modeRadios.forEach(radio => {
      radio.addEventListener('change', (e) => {
        if (e.target.value === 'direct') {
          directContainer.style.display = 'block';
          estimateContainer.style.display = 'none';
        } else {
          directContainer.style.display = 'none';
          estimateContainer.style.display = 'block';
        }
      });
    });
  }
}

/* -------------------------------------------------------------------------- */
/* 3. Smooth Number Count-Up Animation for Results Page                       */
/* -------------------------------------------------------------------------- */
function initCountUpAnimations() {
  const counterElements = document.querySelectorAll('.animate-counter');
  
  counterElements.forEach(el => {
    const targetVal = parseFloat(el.getAttribute('data-target') || '0');
    const isDecimal = targetVal % 1 !== 0 || targetVal < 10;
    const duration = 1200; // ms
    const startTime = performance.now();

    function update(currentTime) {
      const elapsed = currentTime - startTime;
      const progress = Math.min(elapsed / duration, 1);
      // Ease out cubic
      const easeProgress = 1 - Math.pow(1 - progress, 3);
      const currentVal = easeProgress * targetVal;

      el.textContent = isDecimal ? currentVal.toFixed(2) : Math.round(currentVal).toLocaleString();

      if (progress < 1) {
        requestAnimationFrame(update);
      } else {
        el.textContent = isDecimal ? targetVal.toFixed(2) : Math.round(targetVal).toLocaleString();
      }
    }

    requestAnimationFrame(update);
  });
}

/* -------------------------------------------------------------------------- */
/* 4. Form Validation & Safeguards                                            */
/* -------------------------------------------------------------------------- */
function initFormValidation() {
  const calcForm = document.getElementById('carbon-calculator-form');
  if (!calcForm) return;

  calcForm.addEventListener('submit', (e) => {
    const numericInputs = calcForm.querySelectorAll('input[type="number"]');
    let hasError = false;

    numericInputs.forEach(input => {
      const val = parseFloat(input.value);
      if (!isNaN(val) && val < 0) {
        input.classList.add('is-invalid');
        hasError = true;
      } else {
        input.classList.remove('is-invalid');
      }
    });

    if (hasError) {
      e.preventDefault();
      alert('Please ensure all numerical inputs are positive numbers.');
    }
  });
}

/* -------------------------------------------------------------------------- */
/* 5. Chart.js Initializer (Doughnut & Bar Charts)                           */
/* -------------------------------------------------------------------------- */
function renderResultsCharts(chartData) {
  if (typeof Chart === 'undefined') return;

  const categories = ['Transportation', 'Electricity', 'LPG / Cooking', 'Food', 'Waste', 'Water'];
  const values = [
    chartData.transportation || 0,
    chartData.electricity || 0,
    chartData.lpg || 0,
    chartData.food || 0,
    chartData.waste || 0,
    chartData.water || 0
  ];

  // Natural Earthy Color Palette
  const bgColors = [
    '#B87244', // Warm Terracotta (Transportation)
    '#D4A017', // Solar Ochre (Electricity)
    '#C85A32', // Cooking Flame Amber (LPG)
    '#4E8752', // Foliage Green (Food)
    '#7E6551', // Soil / Compost (Waste)
    '#3E8B9E'  // Stream Aqua (Water)
  ];

  // 1. Doughnut Chart: Emission Breakdown
  const doughnutCtx = document.getElementById('emissionsDoughnutChart');
  if (doughnutCtx) {
    new Chart(doughnutCtx.getContext('2d'), {
      type: 'doughnut',
      data: {
        labels: categories,
        datasets: [{
          data: values,
          backgroundColor: bgColors,
          borderWidth: 2,
          borderColor: '#FFFFFF',
          hoverOffset: 6
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        cutout: '68%',
        plugins: {
          legend: {
            position: 'bottom',
            labels: {
              boxWidth: 12,
              padding: 14,
              font: {
                family: 'Inter',
                size: 12
              }
            }
          },
          tooltip: {
            callbacks: {
              label: function(context) {
                const label = context.label || '';
                const val = context.parsed || 0;
                const total = context.dataset.data.reduce((a, b) => a + b, 0);
                const pct = total > 0 ? ((val / total) * 100).toFixed(1) : 0;
                return ` ${label}: ${val} kg CO2e (${pct}%)`;
              }
            }
          }
        }
      }
    });
  }

  // 2. Bar Chart: Category Quantities
  const barCtx = document.getElementById('emissionsBarChart');
  if (barCtx) {
    new Chart(barCtx.getContext('2d'), {
      type: 'bar',
      data: {
        labels: categories,
        datasets: [{
          label: 'Monthly Emissions (kg CO2e)',
          data: values,
          backgroundColor: bgColors,
          borderRadius: 8,
          borderSkipped: false
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            display: false
          },
          tooltip: {
            callbacks: {
              label: function(context) {
                return ` ${context.parsed.y} kg CO2e`;
              }
            }
          }
        },
        scales: {
          y: {
            beginAtZero: true,
            grid: {
              color: '#EDF2EB'
            },
            ticks: {
              font: { family: 'Inter', size: 11 },
              callback: function(value) { return value + ' kg'; }
            }
          },
          x: {
            grid: { display: false },
            ticks: {
              font: { family: 'Inter', size: 11 }
            }
          }
        }
      }
    });
  }
}

/* -------------------------------------------------------------------------- */
/* 6. Modal Confirmation for Safe Deletion                                   */
/* -------------------------------------------------------------------------- */
let activeDeleteForm = null;

function openConfirmModal(formElement, message) {
  activeDeleteForm = formElement;
  const modal = document.getElementById('confirmDeleteModal');
  const modalText = document.getElementById('modalConfirmText');
  if (modal && modalText) {
    modalText.textContent = message || 'Are you sure you want to permanently delete this record?';
    modal.classList.add('show');
  }
}

function closeConfirmModal() {
  const modal = document.getElementById('confirmDeleteModal');
  if (modal) {
    modal.classList.remove('show');
  }
  activeDeleteForm = null;
}

function executeConfirmedDelete() {
  if (activeDeleteForm) {
    activeDeleteForm.submit();
  }
  closeConfirmModal();
}

function initModalConfirmations() {
  document.addEventListener('click', (e) => {
    const target = e.target.closest('[data-confirm-delete]');
    if (target) {
      e.preventDefault();
      const form = target.closest('form');
      const customMsg = target.getAttribute('data-confirm-message');
      openConfirmModal(form, customMsg);
    }
  });
}
