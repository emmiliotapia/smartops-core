"""
Unit tests para validación de schemas (Pydantic).
Verifica que todos los DTOs funcionen correctamente.
"""

import pytest
from uuid import uuid4
from app.modules.demo.schemas import (
    DemoUploadMetadata,
    NeuralizerRequest,
    MessageRequest,
    MessageResponse,
    DemoSessionResponse,
)


class TestDemoUploadMetadata:
    """Tests para validación de metadatos de carga."""
    
    def test_valid_metadata(self):
        """Debe aceptar metadatos válidos."""
        data = {
            "business_name": "Restaurante La Cosecha",
            "business_type": "restaurante"
        }
        metadata = DemoUploadMetadata(**data)
        assert metadata.business_name == "Restaurante La Cosecha"
        assert metadata.business_type == "restaurante"
    
    def test_missing_business_name(self):
        """Debe rechazar si falta business_name."""
        data = {"business_type": "restaurante"}
        with pytest.raises(ValueError):
            DemoUploadMetadata(**data)
    
    def test_missing_business_type(self):
        """Debe rechazar si falta business_type."""
        data = {"business_name": "Test"}
        with pytest.raises(ValueError):
            DemoUploadMetadata(**data)
    
    def test_empty_business_name(self):
        """Debe rechazar business_name vacío."""
        data = {
            "business_name": "",
            "business_type": "restaurante"
        }
        with pytest.raises(ValueError):
            DemoUploadMetadata(**data)
    
    def test_business_name_too_long(self):
        """Debe rechazar business_name mayor a 255 caracteres."""
        data = {
            "business_name": "x" * 256,
            "business_type": "restaurante"
        }
        with pytest.raises(ValueError):
            DemoUploadMetadata(**data)


class TestNeuralizerRequest:
    """Tests para validación de requests del Neuralizer."""
    
    def test_valid_neuralizer_request(self):
        """Debe aceptar request válida."""
        session_id = str(uuid4())
        data = {
            "session_id": session_id,
            "secret_word": "flash",
            "save_lead": True
        }
        request = NeuralizerRequest(**data)
        assert request.session_id == session_id
        assert request.secret_word == "flash"
        assert request.save_lead is True
    
    def test_missing_session_id(self):
        """Debe rechazar si falta session_id."""
        data = {
            "secret_word": "flash",
            "save_lead": True
        }
        with pytest.raises(ValueError):
            NeuralizerRequest(**data)
    
    def test_missing_secret_word(self):
        """Debe rechazar si falta secret_word."""
        data = {
            "session_id": str(uuid4()),
            "save_lead": True
        }
        with pytest.raises(ValueError):
            NeuralizerRequest(**data)
    
    def test_save_lead_defaults_to_true(self):
        """save_lead debe tener default True."""
        data = {
            "session_id": str(uuid4()),
            "secret_word": "flash"
        }
        request = NeuralizerRequest(**data)
        assert request.save_lead is True


class TestMessageRequest:
    """Tests para validación de requests de mensajes."""
    
    def test_valid_message_request(self):
        """Debe aceptar request válida."""
        session_id = str(uuid4())
        data = {
            "session_id": session_id,
            "message": "¿Cuál es el menú?"
        }
        request = MessageRequest(**data)
        assert request.session_id == session_id
        assert request.message == "¿Cuál es el menú?"
    
    def test_empty_message(self):
        """Debe rechazar mensaje vacío."""
        data = {
            "session_id": str(uuid4()),
            "message": ""
        }
        with pytest.raises(ValueError):
            MessageRequest(**data)
    
    def test_message_too_long(self):
        """Debe rechazar mensaje mayor a 2000 caracteres."""
        data = {
            "session_id": str(uuid4()),
            "message": "x" * 2001
        }
        with pytest.raises(ValueError):
            MessageRequest(**data)
    
    def test_missing_session_id(self):
        """Debe rechazar si falta session_id."""
        data = {"message": "Test"}
        with pytest.raises(ValueError):
            MessageRequest(**data)


class TestMessageResponse:
    """Tests para validación de responses de mensajes."""
    
    def test_valid_message_response(self):
        """Debe crear response válida."""
        session_id = str(uuid4())
        data = {
            "session_id": session_id,
            "response": "Aquí está el contexto encontrado.",
            "business_type": "restaurante"
        }
        response = MessageResponse(**data)
        assert response.session_id == session_id
        assert response.business_type == "restaurante"
    
    def test_missing_response_field(self):
        """Debe rechazar si falta response."""
        data = {
            "session_id": str(uuid4()),
            "business_type": "restaurante"
        }
        with pytest.raises(ValueError):
            MessageResponse(**data)


class TestDemoSessionResponse:
    """Tests para validación de responses de sesión."""
    
    def test_valid_session_response(self):
        """Debe crear response válida."""
        session_id = str(uuid4())
        data = {
            "session_id": session_id,
            "status": "active",
            "message": "Sesión iniciada correctamente"
        }
        response = DemoSessionResponse(**data)
        assert response.session_id == session_id
        assert response.status == "active"
    
    def test_all_fields_required(self):
        """Debe rechazar si falta algún campo requerido."""
        data = {
            "session_id": str(uuid4()),
            "status": "active"
        }
        with pytest.raises(ValueError):
            DemoSessionResponse(**data)
