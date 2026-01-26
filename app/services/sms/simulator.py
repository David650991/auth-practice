"""
Proveedor SMS simulado para desarrollo.
Imprime el código en consola y flash message.
"""

import logging

from .base import SMSProvider, SMSResult

logger = logging.getLogger(__name__)


class SimulatorProvider(SMSProvider):
    """Simulador de SMS para entorno de desarrollo."""
    
    def send_verification_code(self, phone_number: str) -> SMSResult:
        """
        Simula envío de SMS.
        El código se muestra en logs y se retorna para flash message.
        """
        code = self.generate_code()
        
        logger.info(f"[SMS SIMULATOR] Código {code} -> {phone_number}")
        print(f"\n[SMS GATEWAY SIMULATION] Enviando SMS a {phone_number}: {code}\n")
        
        return SMSResult(
            success=True,
            code=code,
            message=f'[DEV MODE] SMS enviado a {phone_number}. Tu código es: {code}'
        )
