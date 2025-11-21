// Sistema GED - Main JavaScript

/**
 * Utility: Check if Bootstrap is available
 */
function isBootstrapAvailable() {
    return typeof bootstrap !== 'undefined';
}

/**
 * Initialize all event listeners on DOMContentLoaded
 */
document.addEventListener('DOMContentLoaded', function() {
    initAutoHideAlerts();
    initLoadingSpinner();
    initFileInputDisplay();
    initTableRowNavigation();
    initBackToTopButton();
    initTooltipsAndPopovers();
});

/**
 * Auto-hide alerts after 5 seconds
 */
function initAutoHideAlerts() {
    const alerts = document.querySelectorAll('.alert:not(.alert-permanent)');
    alerts.forEach(function(alert) {
        setTimeout(function() {
            if (isBootstrapAvailable() && alert.parentElement) {
                try {
                    const bsAlert = new bootstrap.Alert(alert);
                    bsAlert.close();
                } catch (e) {
                    // Fallback: just hide the element
                    alert.style.display = 'none';
                }
            }
        }, 5000);
    });
}

/**
 * Show loading spinner on form submit
 */
function initLoadingSpinner() {
    const forms = document.querySelectorAll('form[data-loading="true"]');
    forms.forEach(function(form) {
        form.addEventListener('submit', function(e) {
            const submitBtn = form.querySelector('button[type="submit"]');
            if (submitBtn) {
                submitBtn.disabled = true;
                const originalText = submitBtn.innerHTML;
                submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Processando...';

                // Restore button after 10 seconds if form hasn't completed
                setTimeout(function() {
                    if (submitBtn.disabled) {
                        submitBtn.disabled = false;
                        submitBtn.innerHTML = originalText;
                    }
                }, 10000);
            }
        });
    });
}

/**
 * Display selected file name on file inputs
 */
function initFileInputDisplay() {
    const fileInputs = document.querySelectorAll('input[type="file"]');
    fileInputs.forEach(function(input) {
        input.addEventListener('change', function(e) {
            const fileName = e.target.files && e.target.files[0] ? e.target.files[0].name : null;
            if (fileName && e.target.id) {
                const label = document.querySelector(`label[for="${e.target.id}"]`);
                if (label) {
                    label.textContent = fileName;
                }
            }
        });
    });
}

/**
 * Enable table row click navigation
 */
function initTableRowNavigation() {
    const clickableRows = document.querySelectorAll('tr[data-href]');
    clickableRows.forEach(function(row) {
        row.style.cursor = 'pointer';
        row.addEventListener('click', function(e) {
            // Don't navigate if clicking on a button or link
            if (e.target.tagName === 'A' || e.target.tagName === 'BUTTON' || e.target.closest('a, button')) {
                return;
            }
            window.location.href = row.dataset.href;
        });
    });
}

/**
 * Add "back to top" button
 */
function initBackToTopButton() {
    const backToTopBtn = document.createElement('button');
    backToTopBtn.innerHTML = '<i class="bi bi-arrow-up"></i>';
    backToTopBtn.className = 'btn btn-primary position-fixed bottom-0 end-0 m-3';
    backToTopBtn.style.display = 'none';
    backToTopBtn.style.zIndex = '1000';
    backToTopBtn.setAttribute('aria-label', 'Voltar ao topo');
    backToTopBtn.onclick = scrollToTop;
    document.body.appendChild(backToTopBtn);

    window.addEventListener('scroll', function() {
        if (window.pageYOffset > 300) {
            backToTopBtn.style.display = 'block';
        } else {
            backToTopBtn.style.display = 'none';
        }
    });
}

/**
 * Initialize Bootstrap tooltips and popovers
 */
function initTooltipsAndPopovers() {
    if (!isBootstrapAvailable()) return;

    try {
        const tooltipTriggerList = document.querySelectorAll('[data-bs-toggle="tooltip"]');
        tooltipTriggerList.forEach(function(tooltipTriggerEl) {
            new bootstrap.Tooltip(tooltipTriggerEl);
        });

        const popoverTriggerList = document.querySelectorAll('[data-bs-toggle="popover"]');
        popoverTriggerList.forEach(function(popoverTriggerEl) {
            new bootstrap.Popover(popoverTriggerEl);
        });
    } catch (e) {
        console.warn('Error initializing Bootstrap tooltips/popovers:', e);
    }
}

// ==========================================
// UTILITY FUNCTIONS
// ==========================================

/**
 * Confirm delete actions
 */
function confirmDelete(message) {
    return confirm(message || 'Tem certeza que deseja excluir este item?');
}

/**
 * Format file size to human readable
 */
function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
}

/**
 * Auto-refresh countdown
 */
function startAutoRefresh(seconds, url) {
    let remaining = seconds;
    const countdownEl = document.getElementById('countdown');

    const interval = setInterval(function() {
        remaining--;
        if (countdownEl) {
            countdownEl.textContent = remaining;
        }

        if (remaining <= 0) {
            clearInterval(interval);
            window.location.href = url || window.location.href;
        }
    }, 1000);

    return interval;
}

/**
 * Copy text to clipboard
 */
function copyToClipboard(text) {
    if (!navigator.clipboard) {
        // Fallback for older browsers
        const textArea = document.createElement('textarea');
        textArea.value = text;
        document.body.appendChild(textArea);
        textArea.select();
        try {
            document.execCommand('copy');
            showToast('Copiado para a área de transferência!', 'success');
        } catch (err) {
            showToast('Erro ao copiar', 'danger');
        }
        document.body.removeChild(textArea);
        return;
    }

    navigator.clipboard.writeText(text).then(function() {
        showToast('Copiado para a área de transferência!', 'success');
    }).catch(function(err) {
        showToast('Erro ao copiar: ' + err, 'danger');
    });
}

/**
 * Show toast notification
 */
function showToast(message, type = 'info') {
    const toastContainer = document.getElementById('toast-container') || createToastContainer();

    const toast = document.createElement('div');
    toast.className = `toast align-items-center text-white bg-${type} border-0`;
    toast.setAttribute('role', 'alert');
    toast.setAttribute('aria-live', 'assertive');
    toast.setAttribute('aria-atomic', 'true');

    toast.innerHTML = `
        <div class="d-flex">
            <div class="toast-body">${message}</div>
            <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Fechar"></button>
        </div>
    `;

    toastContainer.appendChild(toast);

    if (isBootstrapAvailable()) {
        try {
            const bsToast = new bootstrap.Toast(toast);
            bsToast.show();

            toast.addEventListener('hidden.bs.toast', function() {
                toast.remove();
            });
        } catch (e) {
            // Fallback: show for 3 seconds then remove
            toast.style.display = 'block';
            setTimeout(function() { toast.remove(); }, 3000);
        }
    } else {
        toast.style.display = 'block';
        setTimeout(function() { toast.remove(); }, 3000);
    }
}

/**
 * Create toast container if not exists
 */
function createToastContainer() {
    const container = document.createElement('div');
    container.id = 'toast-container';
    container.className = 'toast-container position-fixed top-0 end-0 p-3';
    container.style.zIndex = '9999';
    document.body.appendChild(container);
    return container;
}

/**
 * Filter table rows by text content
 */
function filterTable(inputId, tableId, column = 0) {
    const input = document.getElementById(inputId);
    const table = document.getElementById(tableId);

    if (!input || !table) {
        console.warn('filterTable: Element not found', { inputId, tableId });
        return;
    }

    const filter = input.value.toUpperCase();
    const rows = table.getElementsByTagName('tr');

    for (let i = 1; i < rows.length; i++) {
        const cells = rows[i].getElementsByTagName('td');
        if (cells.length > column) {
            const cellText = cells[column].textContent || cells[column].innerText;
            rows[i].style.display = cellText.toUpperCase().indexOf(filter) > -1 ? '' : 'none';
        }
    }
}

/**
 * Debounce function for performance optimization
 */
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

/**
 * Format date to Brazilian format
 */
function formatDateBR(dateString) {
    if (!dateString) return '-';
    const date = new Date(dateString);
    return isNaN(date.getTime()) ? '-' : date.toLocaleDateString('pt-BR');
}

/**
 * Format datetime to Brazilian format
 */
function formatDateTimeBR(dateString) {
    if (!dateString) return '-';
    const date = new Date(dateString);
    return isNaN(date.getTime()) ? '-' : date.toLocaleDateString('pt-BR') + ' ' + date.toLocaleTimeString('pt-BR');
}

/**
 * Validate form before submit
 */
function validateForm(formId, rules) {
    const form = document.getElementById(formId);
    if (!form) {
        console.warn('validateForm: Form not found', formId);
        return false;
    }

    let isValid = true;

    Object.keys(rules).forEach(function(fieldName) {
        const field = form.querySelector(`[name="${fieldName}"]`);
        const rule = rules[fieldName];

        if (!field) return;

        // Clear previous errors
        field.classList.remove('is-invalid');
        const errorDiv = field.parentElement.querySelector('.invalid-feedback');
        if (errorDiv) errorDiv.remove();

        // Required validation
        if (rule.required && !field.value.trim()) {
            showFieldError(field, rule.message || 'Este campo é obrigatório');
            isValid = false;
            return;
        }

        // Min length validation
        if (rule.minLength && field.value.length < rule.minLength) {
            showFieldError(field, `Mínimo ${rule.minLength} caracteres`);
            isValid = false;
            return;
        }

        // Email validation
        if (rule.email && field.value && !isValidEmail(field.value)) {
            showFieldError(field, 'Email inválido');
            isValid = false;
            return;
        }

        // Custom validation
        if (rule.custom && !rule.custom(field.value)) {
            showFieldError(field, rule.message || 'Valor inválido');
            isValid = false;
        }
    });

    return isValid;
}

/**
 * Show field validation error
 */
function showFieldError(field, message) {
    field.classList.add('is-invalid');
    const errorDiv = document.createElement('div');
    errorDiv.className = 'invalid-feedback';
    errorDiv.textContent = message;
    field.parentElement.appendChild(errorDiv);
}

/**
 * Validate email format
 */
function isValidEmail(email) {
    const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return re.test(email);
}

// ==========================================
// MODAL HELPERS
// ==========================================

/**
 * Show Bootstrap modal
 */
function showModal(modalId) {
    const modalEl = document.getElementById(modalId);
    if (!modalEl) {
        console.warn('showModal: Modal not found', modalId);
        return;
    }

    if (isBootstrapAvailable()) {
        try {
            const modal = new bootstrap.Modal(modalEl);
            modal.show();
        } catch (e) {
            console.error('Error showing modal:', e);
        }
    }
}

/**
 * Hide Bootstrap modal
 */
function hideModal(modalId) {
    const modalEl = document.getElementById(modalId);
    if (!modalEl || !isBootstrapAvailable()) return;

    try {
        const modal = bootstrap.Modal.getInstance(modalEl);
        if (modal) modal.hide();
    } catch (e) {
        console.error('Error hiding modal:', e);
    }
}

// ==========================================
// DOCUMENT & PRINT HELPERS
// ==========================================

/**
 * Print current document
 */
function printDocument() {
    window.print();
}

/**
 * Export table to CSV file
 */
function exportTableToCSV(tableId, filename = 'export.csv') {
    const table = document.getElementById(tableId);
    if (!table) {
        console.warn('exportTableToCSV: Table not found', tableId);
        return;
    }

    const rows = table.querySelectorAll('tr');
    if (rows.length === 0) {
        showToast('Nenhum dado para exportar', 'warning');
        return;
    }

    const csv = [];

    rows.forEach(function(row) {
        const cols = row.querySelectorAll('td, th');
        const rowData = [];
        cols.forEach(function(col) {
            rowData.push('"' + col.textContent.trim().replace(/"/g, '""') + '"');
        });
        csv.push(rowData.join(','));
    });

    const csvContent = csv.join('\n');
    const blob = new Blob(['\ufeff' + csvContent], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement('a');
    link.href = URL.createObjectURL(blob);
    link.download = filename;
    link.click();

    showToast('Arquivo exportado com sucesso!', 'success');
}

/**
 * Scroll to top of page smoothly
 */
function scrollToTop() {
    window.scrollTo({ top: 0, behavior: 'smooth' });
}

// ==========================================
// AJAX HELPER
// ==========================================

/**
 * Fetch JSON with error handling
 */
async function fetchJSON(url, options = {}) {
    const defaultOptions = {
        headers: {
            'Content-Type': 'application/json'
        },
        credentials: 'include'
    };

    try {
        const response = await fetch(url, { ...defaultOptions, ...options });

        if (!response.ok) {
            const errorMessages = {
                400: 'Requisição inválida',
                401: 'Não autorizado',
                403: 'Acesso negado',
                404: 'Recurso não encontrado',
                500: 'Erro interno do servidor'
            };
            throw new Error(errorMessages[response.status] || `Erro HTTP: ${response.status}`);
        }

        return await response.json();
    } catch (error) {
        if (error.name === 'TypeError') {
            throw new Error('Erro de conexão. Verifique sua internet.');
        }
        throw error;
    }
}

/**
 * Global error handler for unhandled errors
 */
window.addEventListener('error', function(e) {
    console.error('Unhandled error:', e.error);
});

window.addEventListener('unhandledrejection', function(e) {
    console.error('Unhandled promise rejection:', e.reason);
});
