"""
Tests para el servicio SMS.
"""

import pytest


class TestSMSProviderFactory:
    """Tests para get_sms_provider."""
    
    def test_default_provider_is_simulator(self):
        from app.services.sms import get_sms_provider, SimulatorProvider
        
        config = {}
        provider = get_sms_provider(config)
        
        assert isinstance(provider, SimulatorProvider)
    
    def test_explicit_simulator_provider(self):
        from app.services.sms import get_sms_provider, SimulatorProvider
        
        config = {'SMS_PROVIDER': 'simulator'}
        provider = get_sms_provider(config)
        
        assert isinstance(provider, SimulatorProvider)
    
    def test_twilio_provider_instantiation(self):
        from app.services.sms import get_sms_provider, TwilioProvider
        
        config = {
            'SMS_PROVIDER': 'twilio',
            'TWILIO_ACCOUNT_SID': 'test_sid',
            'TWILIO_AUTH_TOKEN': 'test_token',
            'TWILIO_FROM_NUMBER': '+1234567890'
        }
        provider = get_sms_provider(config)
        
        assert isinstance(provider, TwilioProvider)


class TestSimulatorProvider:
    """Tests para SimulatorProvider."""
    
    def test_send_returns_success(self):
        from app.services.sms import SimulatorProvider
        
        provider = SimulatorProvider()
        result = provider.send_verification_code('+521234567890')
        
        assert result.success is True
        assert len(result.code) == 6
        assert result.code.isdigit()
    
    def test_send_returns_message_with_code(self):
        from app.services.sms import SimulatorProvider
        
        provider = SimulatorProvider()
        result = provider.send_verification_code('+521234567890')
        
        assert result.code in result.message


class TestSMSResult:
    """Tests para SMSResult dataclass."""
    
    def test_sms_result_creation(self):
        from app.services.sms.base import SMSResult
        
        result = SMSResult(success=True, code='123456', message='Sent')
        
        assert result.success is True
        assert result.code == '123456'
        assert result.message == 'Sent'


class TestCodeGeneration:
    """Tests para generación de códigos."""
    
    def test_generate_code_length(self):
        from app.services.sms.base import SMSProvider
        
        code = SMSProvider.generate_code()
        
        assert len(code) == 6
    
    def test_generate_code_is_numeric(self):
        from app.services.sms.base import SMSProvider
        
        code = SMSProvider.generate_code()
        
        assert code.isdigit()
    
    def test_generate_code_range(self):
        from app.services.sms.base import SMSProvider
        
        code = SMSProvider.generate_code()
        
        assert 100000 <= int(code) <= 999999
