"""
Servicio SMS configurable.
Expone una interfaz unificada que selecciona el proveedor según configuración.
"""

from .base import SMSProvider
from .simulator import SimulatorProvider
from .twilio_provider import TwilioProvider

__all__ = [
    'SMSProvider',
    'SimulatorProvider',
    'TwilioProvider',
    'get_sms_provider',
]


def get_sms_provider(app_config) -> SMSProvider:
    """
    Factory que retorna el proveedor SMS según configuración.
    
    Args:
        app_config: Objeto de configuración Flask (current_app.config)
    
    Returns:
        SMSProvider: Instancia del proveedor configurado
    """
    provider_name = app_config.get('SMS_PROVIDER', 'simulator')
    
    if provider_name == 'twilio':
        return TwilioProvider(
            account_sid=app_config.get('TWILIO_ACCOUNT_SID'),
            auth_token=app_config.get('TWILIO_AUTH_TOKEN'),
            from_number=app_config.get('TWILIO_FROM_NUMBER')
        )
    
    # Default: simulador para desarrollo
    return SimulatorProvider()
