// ===== CONFIGURACIÓN GLOBAL =====
const CONFIG = {
    API_BASE: '',
    ITEMS_PER_PAGE: 10,
    ANIMATION_DURATION: 300,
    DEBOUNCE_DELAY: 500
};

// ===== ESTADO GLOBAL =====
let appState = {
    datosCargados: 10,
    isLoading: false,
    currentData: null
};

// ===== UTILIDADES =====
const Utils = {
    // Formatear números
    formatNumber: (num, decimals = 0) => {
        if (num === null || num === undefined) return 'N/A';
        return new Intl.NumberFormat('es-CO', {
            minimumFractionDigits: decimals,
            maximumFractionDigits: decimals
        }).format(num);
    },

    // Formatear moneda
    formatCurrency: (amount, currency = 'COP') => {
        if (amount === null || amount === undefined) return 'N/A';
        const symbol = currency === 'COP' ? '$' : '$';
        return `${symbol}${Utils.formatNumber(amount, currency === 'USD' ? 2 : 0)}`;
    },

    // Debounce function
    debounce: (func, wait) => {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    },

    // Mostrar loading en botón
    setButtonLoading: (button, isLoading, originalText = '') => {
        if (isLoading) {
            button.dataset.originalText = button.innerHTML;
            button.innerHTML = '<i class="fas fa-spinner fa-spin me-1"></i>Cargando...';
            button.disabled = true;
            button.classList.add('loading');
        } else {
            button.innerHTML = button.dataset.originalText || originalText;
            button.disabled = false;
            button.classList.remove('loading');
        }
    },

    // Mostrar notificación
    showNotification: (message, type = 'info', duration = 3000) => {
        const notification = document.createElement('div');
        notification.className = `alert alert-${type} position-fixed`;
        notification.style.cssText = `
            top: 20px;
            right: 20px;
            z-index: 9999;
            min-width: 300px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        `;
        notification.innerHTML = `
            <div class="d-flex align-items-center">
                <i class="fas fa-${type === 'success' ? 'check-circle' : type === 'error' ? 'exclamation-circle' : 'info-circle'} me-2"></i>
                ${message}
                <button type="button" class="btn-close ms-auto" onclick="this.parentElement.parentElement.remove()"></button>
            </div>
        `;
        
        document.body.appendChild(notification);
        
        // Auto remove
        setTimeout(() => {
            if (notification.parentElement) {
                notification.remove();
            }
        }, duration);
    },

    // Truncar texto
    truncateText: (text, maxLength = 50) => {
        if (!text || text.length <= maxLength) return text || 'N/A';
        return text.substring(0, maxLength) + '...';
    }
};

// ===== API CLIENT =====
const ApiClient = {
    async request(endpoint, options = {}) {
        try {
            const response = await fetch(`${CONFIG.API_BASE}${endpoint}`, {
                headers: {
                    'Content-Type': 'application/json',
                    ...options.headers
                },
                ...options
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            return await response.json();
        } catch (error) {
            console.error('API Request failed:', error);
            throw error;
        }
    },

    // Obtener datos de tabla
    async getTableData(limite = CONFIG.ITEMS_PER_PAGE) {
        return this.request(`/api/tabla?limite=${limite}`);
    },

    // Buscar viviendas
    async searchHouses(filters) {
        const params = new URLSearchParams();
        Object.entries(filters).forEach(([key, value]) => {
            if (value !== null && value !== undefined && value !== '') {
                params.append(key, value);
            }
        });
        return this.request(`/api/buscar?${params.toString()}`);
    },

    // Actualizar datos
    async updateData() {
        return this.request('/api/actualizar');
    },

    // Obtener todos los datos
    async getAllData() {
        return this.request('/api/datos');
    }
};

// ===== COMPONENTES DE UI =====
const UIComponents = {
    // Crear fila de tabla
    createTableRow: (row) => {
        const tr = document.createElement('tr');
        tr.className = 'fade-in-up';
        tr.innerHTML = `
            <td>${row.area || 'N/A'}</td>
            <td>${Utils.formatCurrency(row.precio, 'COP')}</td>
            <td>${Utils.formatCurrency(row.precio_USD, 'USD')}</td>
            <td><span class="badge bg-primary">${row.tipo_vivienda || 'N/A'}</span></td>
            <td title="${row.descripcion || 'N/A'}">${Utils.truncateText(row.descripcion)}</td>
        `;
        return tr;
    },

    // Crear mensaje de error en tabla
    createErrorRow: (message, colspan = 5) => {
        const tr = document.createElement('tr');
        tr.innerHTML = `<td colspan="${colspan}" class="text-center text-danger py-4">
            <i class="fas fa-exclamation-triangle me-2"></i>${message}
        </td>`;
        return tr;
    },

    // Crear skeleton loading
    createSkeletonRow: (colspan = 5) => {
        const tr = document.createElement('tr');
        tr.className = 'skeleton-row';
        tr.innerHTML = `<td colspan="${colspan}" class="text-center py-4">
            <div class="spinner-border text-primary" role="status">
                <span class="visually-hidden">Cargando...</span>
            </div>
        </td>`;
        return tr;
    }
};

// ===== CONTROLADORES DE DATOS =====
const DataController = {
    // Cargar datos de tabla
    async loadTableData(limite = CONFIG.ITEMS_PER_PAGE) {
        const tbody = document.querySelector('#datosTabla tbody');
        if (!tbody) return;

        try {
            // Mostrar loading
            tbody.innerHTML = '';
            tbody.appendChild(UIComponents.createSkeletonRow());

            const data = await ApiClient.getTableData(limite);
            
            // Limpiar tabla
            tbody.innerHTML = '';

            if (data.datos && data.datos.length > 0) {
                data.datos.forEach((row, index) => {
                    const tr = UIComponents.createTableRow(row);
                    // Agregar delay para animación escalonada
                    setTimeout(() => tbody.appendChild(tr), index * 50);
                });
                appState.currentData = data.datos;
            } else {
                tbody.appendChild(UIComponents.createErrorRow('No hay datos disponibles'));
            }

        } catch (error) {
            console.error('Error cargando datos:', error);
            tbody.innerHTML = '';
            tbody.appendChild(UIComponents.createErrorRow('Error cargando datos'));
            Utils.showNotification('Error al cargar los datos de la tabla', 'danger');
        }
    },

    // Cargar más datos
    async loadMoreData() {
        appState.datosCargados += CONFIG.ITEMS_PER_PAGE;
        await this.loadTableData(appState.datosCargados);
    },

    // Actualizar todos los datos
    async updateAllData() {
        const updateButton = document.querySelector('[onclick="actualizarDatos()"]');
        
        if (!updateButton || appState.isLoading) return;

        appState.isLoading = true;
        Utils.setButtonLoading(updateButton, true);

        try {
            const data = await ApiClient.updateData();

            if (data.success) {
                Utils.showNotification('Datos actualizados correctamente', 'success');
                // Recargar la página después de un breve delay
                setTimeout(() => {
                    window.location.reload();
                }, 1000);
            } else {
                throw new Error(data.error || 'Error desconocido');
            }

        } catch (error) {
            console.error('Error actualizando datos:', error);
            Utils.showNotification(`Error al actualizar: ${error.message}`, 'danger');
        } finally {
            appState.isLoading = false;
            Utils.setButtonLoading(updateButton, false);
        }
    }
};

// ===== FUNCIONES GLOBALES (para mantener compatibilidad) =====
window.cargarDatosTabla = (limite) => DataController.loadTableData(limite);
window.cargarMasDatos = () => DataController.loadMoreData();
window.actualizarDatos = () => DataController.updateAllData();

// ===== INICIALIZACIÓN AL CARGAR DOM =====
document.addEventListener('DOMContentLoaded', () => {
    App.init();
});

// ===== MANEJO DE ERRORES GLOBALES =====
window.addEventListener('error', (e) => {
    console.error('Error global:', e.error);
    Utils.showNotification('Ha ocurrido un error inesperado', 'danger');
});

window.addEventListener('unhandledrejection', (e) => {
    console.error('Promise rechazada:', e.reason);
    Utils.showNotification('Error de conexión', 'warning');
});