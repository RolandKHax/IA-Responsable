/**
 * JavaScript principal
 * ENSA Béni Mellal - Système IA Responsable
 */

// ==================== INITIALISATION ====================

document.addEventListener('DOMContentLoaded', function() {
    // Initialiser les tooltips Bootstrap
    initializeTooltips();
    
    // Initialiser les confirmations
    initializeConfirmations();
    
    // Auto-hide des alertes
    autoHideAlerts();
    
    // Améliorer les formulaires
    enhanceForms();
    
    // Compter les caractères
    initializeCharacterCounters();
});

// ==================== TOOLTIPS ====================

function initializeTooltips() {
    const tooltipTriggerList = [].slice.call(
        document.querySelectorAll('[data-bs-toggle="tooltip"]')
    );
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
}

// ==================== CONFIRMATIONS ====================

function initializeConfirmations() {
    // Confirmation pour suppressions
    const deleteButtons = document.querySelectorAll('[data-confirm]');
    deleteButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            const message = this.getAttribute('data-confirm') || 
                          'Êtes-vous sûr de vouloir effectuer cette action ?';
            if (!confirm(message)) {
                e.preventDefault();
            }
        });
    });
}

// ==================== AUTO-HIDE ALERTES ====================

function autoHideAlerts() {
    const alerts = document.querySelectorAll('.alert:not(.alert-permanent)');
    alerts.forEach(alert => {
        setTimeout(() => {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }, 5000); // 5 secondes
    });
}

// ==================== AMÉLIORATION DES FORMULAIRES ====================

function enhanceForms() {
    // Validation en temps réel
    const forms = document.querySelectorAll('.needs-validation');
    forms.forEach(form => {
        form.addEventListener('submit', function(event) {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            form.classList.add('was-validated');
        });
    });
    
    // Désactiver le bouton submit après soumission
    const submitButtons = document.querySelectorAll('form button[type="submit"]');
    submitButtons.forEach(button => {
        const form = button.closest('form');
        if (form) {
            form.addEventListener('submit', function() {
                button.disabled = true;
                button.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Envoi...';
            });
        }
    });
}

// ==================== COMPTEURS DE CARACTÈRES ====================

function initializeCharacterCounters() {
    const textareas = document.querySelectorAll('textarea[data-max-length]');
    textareas.forEach(textarea => {
        const maxLength = parseInt(textarea.getAttribute('data-max-length'));
        
        // Créer le compteur
        const counter = document.createElement('div');
        counter.className = 'form-text text-end';
        counter.innerHTML = `<span class="char-count">0</span> / ${maxLength} caractères`;
        textarea.parentNode.appendChild(counter);
        
        // Mettre à jour le compteur
        const updateCounter = () => {
            const count = textarea.value.length;
            const charCountSpan = counter.querySelector('.char-count');
            charCountSpan.textContent = count;
            
            // Changer la couleur si proche de la limite
            if (count > maxLength * 0.9) {
                charCountSpan.classList.add('text-danger');
            } else if (count > maxLength * 0.75) {
                charCountSpan.classList.add('text-warning');
            } else {
                charCountSpan.classList.remove('text-danger', 'text-warning');
            }
        };
        
        textarea.addEventListener('input', updateCounter);
        updateCounter();
    });
}

// ==================== COPIER DANS LE PRESSE-PAPIERS ====================

function copyToClipboard(text) {
    if (navigator.clipboard) {
        navigator.clipboard.writeText(text).then(() => {
            showToast('Copié dans le presse-papiers !', 'success');
        }).catch(err => {
            console.error('Erreur de copie:', err);
            showToast('Erreur lors de la copie', 'danger');
        });
    } else {
        // Fallback pour navigateurs anciens
        const textarea = document.createElement('textarea');
        textarea.value = text;
        document.body.appendChild(textarea);
        textarea.select();
        document.execCommand('copy');
        document.body.removeChild(textarea);
        showToast('Copié !', 'success');
    }
}

// Attacher aux boutons de copie
document.addEventListener('DOMContentLoaded', function() {
    const copyButtons = document.querySelectorAll('[data-copy]');
    copyButtons.forEach(button => {
        button.addEventListener('click', function() {
            const targetId = this.getAttribute('data-copy');
            const target = document.getElementById(targetId);
            if (target) {
                copyToClipboard(target.textContent || target.value);
            }
        });
    });
});

// ==================== TOASTS ====================

function showToast(message, type = 'info') {
    // Créer le conteneur de toasts s'il n'existe pas
    let toastContainer = document.querySelector('.toast-container');
    if (!toastContainer) {
        toastContainer = document.createElement('div');
        toastContainer.className = 'toast-container position-fixed bottom-0 end-0 p-3';
        document.body.appendChild(toastContainer);
    }
    
    // Créer le toast
    const toastHtml = `
        <div class="toast align-items-center text-white bg-${type} border-0" role="alert">
            <div class="d-flex">
                <div class="toast-body">
                    ${message}
                </div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" 
                        data-bs-dismiss="toast"></button>
            </div>
        </div>
    `;
    
    toastContainer.insertAdjacentHTML('beforeend', toastHtml);
    const toastElement = toastContainer.lastElementChild;
    const toast = new bootstrap.Toast(toastElement);
    toast.show();
    
    // Supprimer après fermeture
    toastElement.addEventListener('hidden.bs.toast', function() {
        toastElement.remove();
    });
}

// ==================== RECHERCHE EN TEMPS RÉEL ====================

function initializeLiveSearch(inputId, targetSelector, searchKeys) {
    const input = document.getElementById(inputId);
    if (!input) return;
    
    input.addEventListener('input', function() {
        const searchTerm = this.value.toLowerCase();
        const items = document.querySelectorAll(targetSelector);
        
        items.forEach(item => {
            const text = searchKeys
                .map(key => item.getAttribute(`data-${key}`) || '')
                .join(' ')
                .toLowerCase();
            
            if (text.includes(searchTerm)) {
                item.style.display = '';
            } else {
                item.style.display = 'none';
            }
        });
    });
}

// ==================== FILTRES ====================

function initializeFilters() {
    const filterSelects = document.querySelectorAll('[data-filter]');
    filterSelects.forEach(select => {
        select.addEventListener('change', function() {
            const filterKey = this.getAttribute('data-filter');
            const filterValue = this.value;
            const targetSelector = this.getAttribute('data-target');
            const items = document.querySelectorAll(targetSelector);
            
            items.forEach(item => {
                const itemValue = item.getAttribute(`data-${filterKey}`);
                if (!filterValue || itemValue === filterValue) {
                    item.style.display = '';
                } else {
                    item.style.display = 'none';
                }
            });
        });
    });
}

// ==================== GRAPHIQUES (Chart.js) ====================

function createChart(canvasId, type, data, options = {}) {
    const ctx = document.getElementById(canvasId);
    if (!ctx) return null;
    
    // Vérifier si Chart.js est chargé
    if (typeof Chart === 'undefined') {
        console.warn('Chart.js n\'est pas chargé');
        return null;
    }
    
    return new Chart(ctx, {
        type: type,
        data: data,
        options: {
            responsive: true,
            maintainAspectRatio: true,
            ...options
        }
    });
}

// ==================== UTILITAIRES ====================

// Formater les dates
function formatDate(date, format = 'fr-FR') {
    const d = new Date(date);
    return d.toLocaleDateString(format);
}

// Formater les nombres
function formatNumber(num, decimals = 0) {
    return num.toFixed(decimals).replace(/\B(?=(\d{3})+(?!\d))/g, ' ');
}

// Débounce pour optimiser les événements
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// ==================== EXPORT DE DONNÉES ====================

function exportToJSON(data, filename = 'export.json') {
    const json = JSON.stringify(data, null, 2);
    const blob = new Blob([json], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    
    const link = document.createElement('a');
    link.href = url;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
}

function exportToCSV(data, filename = 'export.csv') {
    // Conversion simple tableau d'objets -> CSV
    if (!data || !data.length) return;
    
    const headers = Object.keys(data[0]);
    const csv = [
        headers.join(','),
        ...data.map(row => 
            headers.map(header => 
                JSON.stringify(row[header] || '')
            ).join(',')
        )
    ].join('\n');
    
    const blob = new Blob([csv], { type: 'text/csv' });
    const url = URL.createObjectURL(blob);
    
    const link = document.createElement('a');
    link.href = url;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
}

// ==================== API CALLS ====================

async function apiCall(endpoint, method = 'GET', data = null) {
    const options = {
        method: method,
        headers: {
            'Content-Type': 'application/json',
        }
    };
    
    if (data) {
        options.body = JSON.stringify(data);
    }
    
    try {
        const response = await fetch(endpoint, options);
        const result = await response.json();
        
        if (!response.ok) {
            throw new Error(result.error || 'Erreur API');
        }
        
        return result;
    } catch (error) {
        console.error('Erreur API:', error);
        showToast(error.message, 'danger');
        throw error;
    }
}

// ==================== VALIDATION CÔTÉ CLIENT ====================

function validateEmail(email) {
    const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return re.test(email);
}

function validatePassword(password) {
    // Au moins 8 caractères, 1 majuscule, 1 minuscule, 1 chiffre
    const re = /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)[a-zA-Z\d@$!%*?&]{8,}$/;
    return re.test(password);
}

// ==================== CONSOLE LOGGER ====================

// Logger personnalisé pour le développement
const logger = {
    info: (msg) => console.log(`ℹ️ [INFO] ${msg}`),
    success: (msg) => console.log(`✅ [SUCCESS] ${msg}`),
    warning: (msg) => console.warn(`⚠️ [WARNING] ${msg}`),
    error: (msg) => console.error(`❌ [ERROR] ${msg}`)
};

// ==================== INITIALISATION GLOBALE ====================

// Exposer certaines fonctions globalement
window.copyToClipboard = copyToClipboard;
window.showToast = showToast;
window.apiCall = apiCall;
window.exportToJSON = exportToJSON;
window.exportToCSV = exportToCSV;
window.logger = logger;