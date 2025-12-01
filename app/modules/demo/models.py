"""
SQLAlchemy ORM models for the Demo module.
Modelos de base de datos para la demostración comercial.
"""

from sqlalchemy import Column, String, Boolean, DateTime, JSON, ForeignKey, Text, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid
from app.database import Base

try:
    from pgvector.sqlalchemy import Vector
except ImportError:
    Vector = None


class DemoSession(Base):
    """
    Controla el ciclo de vida de la sesión de demostración temporal.
    
    Attributes:
        id: Identificador único (UUID) de la sesión.
        active: Indica si la demostración está activa.
        business_type: Tipo de negocio (restaurante, clínica, etc) - metadato para RAG.
        business_name: Nombre del negocio del cliente.
        source_file_path: Ruta al archivo PDF o imagen cargado.
        vector_collection_id: Identificador en la base de datos vectorial (pgvector) para limpieza.
        created_at: Marca de tiempo de creación.
        closed_at: Marca de tiempo de cierre (nullable).
    """
    
    __tablename__ = "demo_sessions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    active = Column(Boolean, default=True, nullable=False, index=True)
    business_type = Column(String(50), nullable=False)  # restaurante, clinica, etc
    business_name = Column(String(255), nullable=False)
    source_file_path = Column(String(500), nullable=True)
    vector_collection_id = Column(String(255), nullable=True)  # ID en pgvector para cleanup
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    closed_at = Column(DateTime(timezone=True), nullable=True)
    
    def __repr__(self):
        return f"<DemoSession(id={self.id}, business_name='{self.business_name}', active={self.active})>"


class DemoLead(Base):
    """
    Registra los datos del prospecto capturado al finalizar la demostración.
    
    Attributes:
        id: Identificador único (UUID) del lead.
        session_id: Referencia a la sesión de demostración (ForeignKey).
        prospect_name: Nombre del prospecto capturado.
        prospect_phone: Número telefónico del prospecto.
        interest_level: Nivel de interés (caliente, tibio, frio).
        notes: Campo JSON para notas adicionales y metadata flexible.
        created_at: Marca de tiempo de creación.
    """
    
    __tablename__ = "demo_leads"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id = Column(UUID(as_uuid=True), ForeignKey("demo_sessions.id"), nullable=False, index=True)
    prospect_name = Column(String(255), nullable=False)
    prospect_phone = Column(String(20), nullable=False)
    interest_level = Column(String(20), nullable=False)  # caliente, tibio, frio
    notes = Column(JSON, default=dict, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    def __repr__(self):
        return f"<DemoLead(id={self.id}, prospect_name='{self.prospect_name}', interest_level='{self.interest_level}')>"


class DemoVector(Base):
    """
    Almacena chunks de texto y embeddings generados del PDF de demostración.
    
    Attributes:
        id: Identificador único (UUID).
        session_id: Referencia a la sesión de demostración (ForeignKey).
        chunk_number: Número secuencial del chunk (para reconstrucción).
        chunk_text: Texto del chunk (máximo MAX_CHUNK_SIZE caracteres).
        embedding: Vector de embedding (1536 dims para text-embedding-3-small).
        chunk_metadata: JSON adicional (source, page, etc).
        created_at: Marca de tiempo de creación.
    """
    
    __tablename__ = "demo_vectors"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id = Column(UUID(as_uuid=True), ForeignKey("demo_sessions.id"), nullable=False, index=True)
    chunk_number = Column(Integer, nullable=False)  # Orden del chunk en el documento
    chunk_text = Column(Text, nullable=False)  # Contenido de texto
    embedding = Column(Vector(1536), nullable=False)  # OpenAI text-embedding-3-small (1536 dims)
    chunk_metadata = Column(JSON, default=dict, nullable=False)  # Metadata flexible (category, source, etc)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    def __repr__(self):
        return f"<DemoVector(id={self.id}, session_id={self.session_id}, chunk_number={self.chunk_number})>"