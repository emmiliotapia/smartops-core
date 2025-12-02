"""
Unit tests para endpoints FastAPI (routers/demo.py).
Verifica THE LOADER, THE SHOW, THE NEURALIZER.
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch, MagicMock
from io import BytesIO
from uuid import uuid4
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.database import Base, get_db
from app.modules.demo.models import DemoSession, DemoLead
from app.modules.demo.schemas import DemoSessionResponse


@pytest.fixture
def client(test_db_engine):
    """Crea cliente de prueba con BD lista."""
    # Override is already done in test_db_engine fixture
    return TestClient(app)


class TestHealthEndpoint:
    """Tests para health check."""
    
    def test_demo_health_check(self, client):
        """Debe retornar healthy."""
        response = client.get("/demo/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["module"] == "demo"


class TestTheLoaderEndpoint:
    """Tests para THE LOADER - POST /demo/upload."""
    
    def test_upload_valid_pdf(self, client, test_db):
        """Debe aceptar PDF válido."""
        pdf_content = b"%PDF-1.4\n%EOF"  # Mock PDF
        
        response = client.post(
            "/demo/upload",
            data={
                "business_name": "Restaurante Test",
                "business_type": "restaurante"
            },
            files={"file": ("menu.pdf", BytesIO(pdf_content), "application/pdf")}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "session_id" in data
        assert data["status"] == "active"
    
    def test_upload_valid_image(self, client):
        """Debe aceptar imagen JPG/PNG."""
        image_content = b"\xFF\xD8\xFF\xE0"  # Mock JPEG
        
        response = client.post(
            "/demo/upload",
            data={
                "business_name": "Clinica Test",
                "business_type": "clinica"
            },
            files={"file": ("photo.jpg", BytesIO(image_content), "image/jpeg")}
        )
        
        assert response.status_code == 200
        assert "session_id" in response.json()
    
    def test_upload_invalid_file_type(self, client):
        """Debe rechazar tipos de archivo inválidos."""
        response = client.post(
            "/demo/upload",
            data={
                "business_name": "Test",
                "business_type": "restaurante"
            },
            files={"file": ("file.txt", BytesIO(b"text"), "text/plain")}
        )
        
        assert response.status_code == 400
        assert "no permitido" in response.json()["detail"].lower()
    
    def test_upload_missing_business_name(self, client):
        """Debe rechazar si falta business_name."""
        response = client.post(
            "/demo/upload",
            data={"business_type": "restaurante"},
            files={"file": ("menu.pdf", BytesIO(b"%PDF"), "application/pdf")}
        )
        
        assert response.status_code == 422  # Validation error
    
    def test_upload_missing_business_type(self, client):
        """Debe rechazar si falta business_type."""
        response = client.post(
            "/demo/upload",
            data={"business_name": "Test"},
            files={"file": ("menu.pdf", BytesIO(b"%PDF"), "application/pdf")}
        )
        
        assert response.status_code == 422
    
    def test_upload_missing_file(self, client):
        """Debe rechazar si falta archivo."""
        response = client.post(
            "/demo/upload",
            data={
                "business_name": "Test",
                "business_type": "restaurante"
            }
        )
        
        assert response.status_code == 422
    
    def test_upload_creates_session_in_db(self, client, test_db):
        """Debe crear sesión en BD."""
        response = client.post(
            "/demo/upload",
            data={
                "business_name": "Test Business",
                "business_type": "restaurante"
            },
            files={"file": ("menu.pdf", BytesIO(b"%PDF"), "application/pdf")}
        )
        
        assert response.status_code == 200
        session_id = response.json()["session_id"]
        
        # Verificar en BD
        session = test_db.query(DemoSession).filter_by(id=session_id).first()
        assert session is not None
        assert session.business_name == "Test Business"
        assert session.active is True


class TestTheShowEndpoint:
    """Tests para THE SHOW - POST /demo/message."""
    
    def test_message_valid_session(self, client, test_db):
        """Debe enviar mensaje a sesión válida."""
        # Crear sesión primero
        session_id = uuid4()
        demo_session = DemoSession(
            id=session_id,
            active=True,
            business_type="restaurante",
            business_name="Test"
        )
        test_db.add(demo_session)
        test_db.commit()
        
        # Enviar mensaje
        response = client.post(
            "/demo/message",
            json={
                "session_id": str(session_id),
                "message": "¿Cuál es el menú de bebidas?"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["session_id"] == str(session_id)
        assert "response" in data
    
    def test_message_invalid_session(self, client):
        """Debe rechazar sesión inexistente."""
        response = client.post(
            "/demo/message",
            json={
                "session_id": str(uuid4()),
                "message": "Test"
            }
        )
        
        assert response.status_code == 404
        assert "no encontrada" in response.json()["detail"].lower()
    
    def test_message_closed_session(self, client, test_db):
        """Debe rechazar sesión cerrada."""
        session_id = uuid4()
        demo_session = DemoSession(
            id=session_id,
            active=False,
            business_type="restaurante",
            business_name="Test"
        )
        test_db.add(demo_session)
        test_db.commit()
        
        response = client.post(
            "/demo/message",
            json={
                "session_id": str(session_id),
                "message": "Test"
            }
        )
        
        assert response.status_code == 400
        assert "cerrada" in response.json()["detail"].lower()
    
    def test_message_empty(self, client, test_db):
        """Debe rechazar mensaje vacío."""
        session_id = uuid4()
        demo_session = DemoSession(
            id=session_id,
            active=True,
            business_type="restaurante",
            business_name="Test"
        )
        test_db.add(demo_session)
        test_db.commit()
        
        response = client.post(
            "/demo/message",
            json={
                "session_id": str(session_id),
                "message": ""
            }
        )
        
        assert response.status_code == 422
    
    def test_message_too_long(self, client, test_db):
        """Debe rechazar mensaje mayor a 2000 caracteres."""
        session_id = uuid4()
        demo_session = DemoSession(
            id=session_id,
            active=True,
            business_type="restaurante",
            business_name="Test"
        )
        test_db.add(demo_session)
        test_db.commit()
        
        response = client.post(
            "/demo/message",
            json={
                "session_id": str(session_id),
                "message": "x" * 2001
            }
        )
        
        assert response.status_code == 422
    
    def test_message_response_structure(self, client, test_db):
        """Debe retornar estructura correcta."""
        session_id = uuid4()
        demo_session = DemoSession(
            id=session_id,
            active=True,
            business_type="clinica",
            business_name="San Carlos"
        )
        test_db.add(demo_session)
        test_db.commit()
        
        response = client.post(
            "/demo/message",
            json={
                "session_id": str(session_id),
                "message": "¿Cuáles son tus horarios?"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "session_id" in data
        assert "response" in data
        assert "business_type" in data
        assert data["business_type"] == "clinica"


class TestTheNeuralizerEndpoint:
    """Tests para THE NEURALIZER - POST /demo/reset."""
    
    def test_reset_valid_session(self, client, test_db):
        """Debe cerrar sesión válida."""
        session_id = uuid4()
        demo_session = DemoSession(
            id=session_id,
            active=True,
            business_type="restaurante",
            business_name="Test"
        )
        test_db.add(demo_session)
        test_db.commit()
        
        response = client.post(
            "/demo/reset",
            json={
                "session_id": str(session_id),
                "secret_word": "flash",
                "save_lead": False
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "closed"
        
        # Verificar que se cerró
        session = test_db.query(DemoSession).filter_by(id=session_id).first()
        assert session.active is False
    
    def test_reset_invalid_secret(self, client, test_db):
        """Debe rechazar palabra secreta incorrecta."""
        session_id = uuid4()
        demo_session = DemoSession(
            id=session_id,
            active=True,
            business_type="restaurante",
            business_name="Test"
        )
        test_db.add(demo_session)
        test_db.commit()
        
        response = client.post(
            "/demo/reset",
            json={
                "session_id": str(session_id),
                "secret_word": "incorrect",
                "save_lead": False
            }
        )
        
        assert response.status_code == 403
        assert "incorrecta" in response.json()["detail"].lower()
    
    def test_reset_nonexistent_session(self, client):
        """Debe rechazar sesión inexistente."""
        response = client.post(
            "/demo/reset",
            json={
                "session_id": str(uuid4()),
                "secret_word": "flash",
                "save_lead": False
            }
        )
        
        assert response.status_code == 404
        assert "no encontrada" in response.json()["detail"].lower()
    
    def test_reset_with_save_lead(self, client, test_db):
        """Debe guardar lead al cerrar."""
        session_id = uuid4()
        demo_session = DemoSession(
            id=session_id,
            active=True,
            business_type="restaurante",
            business_name="Test Restaurant"
        )
        test_db.add(demo_session)
        test_db.commit()
        
        response = client.post(
            "/demo/reset",
            json={
                "session_id": str(session_id),
                "secret_word": "flash",
                "save_lead": True
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["lead_saved"] is True
        
        # Verificar que se creó lead
        lead = test_db.query(DemoLead).filter_by(session_id=session_id).first()
        assert lead is not None
    
    def test_reset_response_structure(self, client, test_db):
        """Debe retornar estructura correcta."""
        session_id = uuid4()
        demo_session = DemoSession(
            id=session_id,
            active=True,
            business_type="restaurante",
            business_name="Test"
        )
        test_db.add(demo_session)
        test_db.commit()
        
        response = client.post(
            "/demo/reset",
            json={
                "session_id": str(session_id),
                "secret_word": "flash",
                "save_lead": False
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "session_id" in data
        assert "status" in data
        assert "message" in data
        assert "lead_saved" in data
        assert data["status"] == "closed"


class TestEndpointIntegration:
    """Tests de integración entre endpoints."""
    
    def test_full_demo_workflow(self, client, test_db):
        """Debe completar workflow completo: upload → message → reset."""
        # Step 1: Upload
        upload_response = client.post(
            "/demo/upload",
            data={
                "business_name": "Restaurant Integration Test",
                "business_type": "restaurante"
            },
            files={"file": ("menu.pdf", BytesIO(b"%PDF"), "application/pdf")}
        )
        assert upload_response.status_code == 200
        session_id = upload_response.json()["session_id"]
        
        # Step 2: Send message
        message_response = client.post(
            "/demo/message",
            json={
                "session_id": session_id,
                "message": "¿Tienes vegetariano?"
            }
        )
        assert message_response.status_code == 200
        assert message_response.json()["session_id"] == session_id
        
        # Step 3: Reset/Close
        reset_response = client.post(
            "/demo/reset",
            json={
                "session_id": session_id,
                "secret_word": "flash",
                "save_lead": True
            }
        )
        assert reset_response.status_code == 200
        assert reset_response.json()["status"] == "closed"
