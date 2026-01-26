/**
 * Configuración inyectada desde el backend.
 * El HTML debe definir window.__ENROLL_CONFIG__ antes de cargar este módulo.
 */
export function getConfig() {
    const cfg = window.__ENROLL_CONFIG__;
    if (!cfg) {
        console.error('[CONFIG] No se encontró __ENROLL_CONFIG__ en window');
        return { enrollUrl: '/face-enroll', csrfToken: '' };
    }
    return {
        enrollUrl: cfg.enrollUrl || '/face-enroll',
        csrfToken: cfg.csrfToken || ''
    };
}
