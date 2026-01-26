"""
Proveedor SMS Twilio para producción.
Requiere configuración de credenciales en variables de entorno.
"""

import logging

from .base import SMSProvider, SMSResult

logger = logging.getLogger(__name__)


class TwilioProvider(SMSProvider):
    """Proveedor SMS real usando Twilio API."""
    
    def __init__(self, account_sid: str, auth_token: str, from_number: str):
        self.account_sid = account_sid
        self.auth_token = auth_token
        self.from_number = from_number
        self._client = None
    
    @property
    def client(self):
        """Lazy loading del cliente Twilio."""
        if self._client is None:
            try:
                from twilio.rest import Client
                self._client = Client(self.account_sid, self.auth_token)
            except ImportError:
                logger.error("Twilio no instalado. Ejecutar: pip install twilio")
                raise
        return self._client
    
    def send_verification_code(self, phone_number: str) -> SMSResult:
        """
        Envía SMS real via Twilio.
        
        Args:
            phone_number: Número con formato internacional (+52...)
        """
        code = self.generate_code()
        body = f"Tu código de verificación es: {code}"
        
        try:
            message = self.client.messages.create(
                body=body,
                from_=self.from_number,
                to=phone_number
            )
            
            logger.info(f"SMS enviado: {message.sid} -> {phone_number}")
            
            return SMSResult(
                success=True,
                code=code,
                message='Código enviado. Revisa tu teléfono.'
            )
            
        except Exception as e:
            logger.error(f"Error enviando SMS a {phone_number}: {e}")
            return SMSResult(
                success=False,
                code='',
                message='Error enviando SMS. Intenta de nuevo.'
            )
