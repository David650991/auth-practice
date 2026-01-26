"""
Clase base abstracta para proveedores SMS.
Define la interfaz que todos los proveedores deben implementar.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class SMSResult:
    """Resultado de envío de SMS."""
    success: bool
    code: str
    message: str


class SMSProvider(ABC):
    """Interfaz abstracta para proveedores SMS."""
    
    @abstractmethod
    def send_verification_code(self, phone_number: str) -> SMSResult:
        """
        Envía un código de verificación al número proporcionado.
        
        Args:
            phone_number: Número de teléfono destino
            
        Returns:
            SMSResult con el estado del envío
        """
        pass
    
    @staticmethod
    def generate_code() -> str:
        """Genera un código de 6 dígitos."""
        import random
        return str(random.randint(100000, 999999))
