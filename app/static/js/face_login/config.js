/**
 * Configuración inyectada desde el backend.
 * El HTML debe definir window.__LOGIN_CONFIG__ antes de cargar este módulo.
 */
export function getConfig() {
    const cfg = window.__LOGIN_CONFIG__;
    if (!cfg) {
        console.error('[CONFIG] No se encontró __LOGIN_CONFIG__ en window');
        return { csrfToken: '' };
    }
    return {
        csrfToken: cfg.csrfToken || ''
    };
}
