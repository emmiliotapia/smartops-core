"""
Pydantic schemas for the Demo module.
Esquemas de validación para requests/responses de la demostración.
"""

from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime
from uuid import UUID


class DemoUploadMetadata(BaseModel):
    """
    Esquema para los metadatos de carga de documento/imagen en la demostración.
    
    Attributes:
        business_name: Nombre del negocio del cliente.
        business_type: Tipo de negocio (restaurante, clínica, etc) - contexto para RAG.
    """
    
    business_name: str = Field(..., min_length=1, max_length=255, description="Nombre del negocio")
    business_type: str = Field(
        ...,
        min_length=1,
        max_length=50,
        description="Tipo de negocio (ej: restaurante, clínica, tienda). Contexto para el RAG."
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "business_name": "Restaurante La Cosecha",
                "business_type": "restaurante"
            }
        }


class NeuralizerRequest(BaseModel):
    """
    Esquema para cerrar una sesión de demostración con opción de guardar lead.
    La 'palabra de seguridad' permite validar que solo usuarios autorizados cierren sesiones.
    
    Attributes:
        session_id: Identificador de la sesión a cerrar.
        secret_word: Palabra de seguridad para autorizar el cierre.
        save_lead: Indicador si se debe guardar el lead capturado.
    """
    
    session_id: str = Field(..., description="ID de la sesión de demostración")
    secret_word: str = Field(..., description="Palabra de seguridad para autorizar cierre")
    save_lead: bool = Field(True, description="Si se debe guardar el lead capturado")
    
    class Config:
        json_schema_extra = {
            "example": {
                "session_id": "550e8400-e29b-41d4-a716-446655440000",
                "secret_word": "demo2024",
                "save_lead": True
            }
        }


class DemoSessionResponse(BaseModel):
    """
    Esquema de respuesta después de operaciones en sesiones de demostración.
    
    Attributes:
        session_id: Identificador de la sesión.
        status: Estado de la operación (success, error, pending, etc).
        message: Mensaje descriptivo del resultado.
    """
    
    session_id: str = Field(..., description="ID de la sesión de demostración")
    status: str = Field(..., description="Estado de la operación")
    message: str = Field(..., description="Mensaje descriptivo del resultado")
    
    class Config:
        json_schema_extra = {
            "example": {
                "session_id": "550e8400-e29b-41d4-a716-446655440000",
                "status": "success",
                "message": "Demostración iniciada correctamente"
            }
        }


class DemoSessionCreate(BaseModel):
    """
    Esquema para crear una nueva sesión de demostración.
    """
    
    business_name: str = Field(..., min_length=1, max_length=255)
    business_type: str = Field(..., min_length=1, max_length=50)
    source_file_path: Optional[str] = Field(None, max_length=500)
    
    class Config:
        json_schema_extra = {
            "example": {
                "business_name": "Clínica San Carlos",
                "business_type": "clinica",
                "source_file_path": "/uploads/menu.pdf"
            }
        }


class DemoLeadCreate(BaseModel):
    """
    Esquema para crear un nuevo lead capturado de una demostración.
    """
    
    session_id: str = Field(..., description="ID de la sesión")
    prospect_name: str = Field(..., min_length=1, max_length=255)
    prospect_phone: str = Field(..., min_length=1, max_length=20)
    interest_level: str = Field(..., description="Nivel de interés: caliente, tibio, frio")
    notes: Optional[Dict[str, Any]] = Field(None, description="Notas adicionales")
    
    class Config:
        json_schema_extra = {
            "example": {
                "session_id": "550e8400-e29b-41d4-a716-446655440000",
                "prospect_name": "Juan Pérez",
                "prospect_phone": "+34912345678",
                "interest_level": "caliente",
                "notes": {"demo_impressions": "Muy interesado en automatización"}
            }
        }


class DemoSessionDetail(BaseModel):
    """
    Esquema de respuesta detallada de una sesión de demostración.
    """
    
    id: UUID
    active: bool
    business_type: str
    business_name: str
    source_file_path: Optional[str]
    vector_collection_id: Optional[str]
    created_at: datetime
    closed_at: Optional[datetime]
    
    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "active": True,
                "business_type": "restaurante",
                "business_name": "El Buen Comer",
                "source_file_path": "/uploads/menu.pdf",
                "vector_collection_id": "col_abc123",
                "created_at": "2024-12-01T10:30:00Z",
                "closed_at": None
            }
        }


class DemoLeadDetail(BaseModel):
    """
    Esquema de respuesta detallada de un lead capturado.
    """
    
    id: UUID
    session_id: UUID
    prospect_name: str
    prospect_phone: str
    interest_level: str
    notes: Dict[str, Any]
    created_at: datetime
    
    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": "660e8400-e29b-41d4-a716-446655440001",
                "session_id": "550e8400-e29b-41d4-a716-446655440000",
                "prospect_name": "María García",
                "prospect_phone": "+34912345678",
                "interest_level": "caliente",
                "notes": {"demo_date": "2024-12-01", "duration_minutes": 45},
                "created_at": "2024-12-01T11:00:00Z"
            }
        }


class NeuralizerResponse(BaseModel):
    """
    Esquema de respuesta después de cerrar una sesión (Neuralizer).
    """
    
    session_id: str = Field(..., description="ID de la sesión cerrada")
    status: str = Field(..., description="Estado de la operación")
    message: str = Field(..., description="Mensaje descriptivo")
    lead_saved: bool = Field(..., description="Si se guardó el lead")
    
    class Config:
        json_schema_extra = {
            "example": {
                "session_id": "550e8400-e29b-41d4-a716-446655440000",
                "status": "closed",
                "message": "Sesion cerrada exitosamente",
                "lead_saved": True
            }
        }


class MessageRequest(BaseModel):
    """
    Esquema para enviar un mensaje dentro de una sesión de demostración.
    """
    
    session_id: str = Field(..., description="ID de la sesión de demostración")
    message: str = Field(..., min_length=1, max_length=2000, description="Mensaje del usuario")
    
    class Config:
        json_schema_extra = {
            "example": {
                "session_id": "550e8400-e29b-41d4-a716-446655440000",
                "message": "Quiero ver el menu de bebidas"
            }
        }


class MessageResponse(BaseModel):
    """
    Esquema de respuesta a un mensaje en la demostración.
    """
    
    session_id: str = Field(..., description="ID de la sesión")
    response: str = Field(..., description="Respuesta del bot")
    business_type: str = Field(..., description="Tipo de negocio")
    
    class Config:
        json_schema_extra = {
            "example": {
                "session_id": "550e8400-e29b-41d4-a716-446655440000",
                "response": "Bienvenido a nuestro restaurante. Estos son nuestros mejores vinos.",
                "business_type": "restaurante"
            }
        }
