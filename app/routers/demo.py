"""
Router for Demo module endpoints.
Implementa los 3 endpoints del Quest 1: THE LOADER, THE SHOW, THE NEURALIZER.
Integra RAG service (Quest 2.2) para PDF ingestion y vector search.
"""

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from datetime import datetime
import os
import uuid
from typing import Optional
import logging

from app.database import get_db
from app.modules.demo.models import DemoSession, DemoLead
from app.modules.demo.schemas import (
    DemoUploadMetadata,
    NeuralizerRequest,
    NeuralizerResponse,
    DemoSessionResponse,
    MessageRequest,
    MessageResponse,
)
from app.services.demo_rag import DemoRAGService

logger = logging.getLogger(__name__)

# Router configuration
router = APIRouter(
    prefix="/demo",
    tags=["Quest 1: Demo Comercial"],
)

# Configuración de seguridad
NEURALIZER_SECRET = os.getenv("NEURALIZER_SECRET", "flash")
UPLOAD_DIR = "/tmp/smartops_demo_uploads"


# Utilities
def ensure_upload_dir():
    """Crear directorio de uploads si no existe."""
    os.makedirs(UPLOAD_DIR, exist_ok=True)


# ============================================================================
# ENDPOINT 1: THE LOADER - POST /demo/upload
# ============================================================================
@router.post(
    "/upload",
    response_model=DemoSessionResponse,
    summary="THE LOADER: Cargar documento/imagen para la demostración",
    description="Crea una sesión de demostración con un archivo (PDF/imagen) y metadatos del negocio.",
)
async def upload_demo(
    file: UploadFile = File(...),
    business_name: str = Form(...),
    business_type: str = Form(...),
    db: Session = Depends(get_db),
):
    """
    THE LOADER - Endpoint de ingesta de datos.
    
    Flujo:
    1. Validar que el archivo sea PDF o imagen
    2. Crear sesión DemoSession en base de datos
    3. Guardar archivo en disco
    4. Llamar a DemoRAGService.index_demo_document() para ingesta RAG (Quest 2.2)
    5. Retornar session_id con estadística de chunks indexados
    
    Args:
        file: Archivo a procesar (PDF o imagen)
        business_name: Nombre del negocio
        business_type: Tipo de negocio (restaurante, clinica, etc)
        db: Sesión de base de datos
        
    Returns:
        DemoSessionResponse con session_id y chunks_indexed
    """
    
    try:
        # Validar tipo de archivo (PDF + Imágenes para Vision)
        allowed_types = {"application/pdf", "image/jpeg", "image/png"}
        content_type = file.content_type or ""
        
        # Mapeo de content-type a extensión
        type_to_ext = {
            "application/pdf": ".pdf",
            "image/jpeg": ".jpg",
            "image/png": ".png"
        }
        
        if content_type not in allowed_types:
            raise HTTPException(
                status_code=400,
                detail=f"Tipo de archivo no permitido. Permitidos: PDF, JPEG, PNG. Recibido: {content_type}"
            )
        
        file_extension = type_to_ext.get(content_type, ".bin")
        
        # Crear registro DemoSession en DB
        session_id = str(uuid.uuid4())
        demo_session = DemoSession(
            id=uuid.UUID(session_id),
            active=True,
            business_type=business_type,
            business_name=business_name,
            source_file_path=f"{UPLOAD_DIR}/{session_id}{file_extension}",
            vector_collection_id=f"col_{session_id[:8]}",
        )
        
        db.add(demo_session)
        db.commit()
        db.refresh(demo_session)
        
        # Guardar archivo en disco
        ensure_upload_dir()
        file_path = f"{UPLOAD_DIR}/{session_id}{file_extension}"
        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)
        
        # Integración Quest 2.2: Indexar PDF con RAG
        chunks_indexed = 0
        rag_status = "pending"
        rag_message = "RAG indexing deferred"
        
        try:
            rag_service = DemoRAGService()
            rag_result = rag_service.index_demo_document(
                session_id=uuid.UUID(session_id),
                file_path=file_path,
                db=db
            )
            chunks_indexed = rag_result.get("chunks", 0)
            rag_status = rag_result.get("status", "pending")
            rag_message = rag_result.get("message", "Indexing complete")
            logger.info(f"RAG indexing complete: {chunks_indexed} chunks indexed")
        except Exception as e:
            # No fallar el upload si RAG falla, pero loguear error
            logger.error(f"RAG indexing failed: {str(e)}")
            chunks_indexed = 0
            rag_status = "failed"
            rag_message = f"RAG indexing failed: {str(e)}"
        
        return DemoSessionResponse(
            session_id=str(demo_session.id),
            status="active",
            message=f"Sesion de demo iniciada para {business_name} ({business_type}). {rag_message}"
        )
    
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error en upload_demo: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error al crear sesion: {str(e)}")


# ============================================================================
# ENDPOINT 2: THE SHOW - POST /demo/message
# ============================================================================
@router.post(
    "/message",
    response_model=MessageResponse,
    summary="THE SHOW: Interactuar con el bot demo",
    description="Envía un mensaje a la demostración y recibe una respuesta contextualizada con RAG.",
)
async def send_message(
    request: MessageRequest,
    db: Session = Depends(get_db),
):
    """
    THE SHOW - Endpoint de interacción con bot.
    
    Flujo:
    1. Buscar DemoSession por session_id
    2. Validar que exista y esté activa
    3. Llamar a DemoRAGService.query_demo() para retrieval vectorial (Quest 2.2)
    4. Retornar respuesta contextualizada con chunks más relevantes
    
    Args:
        request: MessageRequest con session_id y message
        db: Sesión de base de datos
        
    Returns:
        MessageResponse con la respuesta del bot (contexto RAG)
    """
    
    try:
        # Buscar sesión en DB
        demo_session = db.query(DemoSession).filter(
            DemoSession.id == request.session_id
        ).first()
        
        if not demo_session:
            raise HTTPException(
                status_code=404,
                detail=f"Sesion {request.session_id} no encontrada"
            )
        
        if not demo_session.active:
            raise HTTPException(
                status_code=400,
                detail="La sesion de demo ha sido cerrada"
            )
        
        # Integración Quest 2.2: Buscar contexto en RAG
        bot_response = ""
        try:
            rag_service = DemoRAGService()
            # Retrieval vectorial
            context = rag_service.query_demo(
                session_id=request.session_id,
                question=request.message,
                db=db
            )
            # En producción, aquí iría LLM para generar respuesta con contexto
            # Por ahora, retornamos el contexto RAG directamente
            bot_response = f"Contexto encontrado:\n\n{context}"
            logger.info(f"RAG query executed for session {request.session_id}")
        except Exception as e:
            logger.error(f"RAG query failed: {str(e)}")
            # Fallback a respuesta mock si RAG falla
            bot_response = f"Lo siento, no pude recuperar contexto del documento: {str(e)}"
        
        return MessageResponse(
            session_id=str(demo_session.id),
            response=bot_response,
            business_type=demo_session.business_type
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error en send_message: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error al procesar mensaje: {str(e)}")


# ============================================================================
# ENDPOINT 3: THE NEURALIZER - POST /demo/reset
# ============================================================================
@router.post(
    "/reset",
    response_model=NeuralizerResponse,
    summary="THE NEURALIZER: Cerrar y limpiar sesion de demo",
    description="Cierra la sesion de demostración, valida palabra secreta, limpia vectores RAG, y opcionalmente guarda el lead.",
)
async def neuralizer_reset(
    request: NeuralizerRequest,
    db: Session = Depends(get_db),
):
    """
    THE NEURALIZER - Endpoint de cierre de sesión.
    
    Flujo:
    1. Validar palabra secreta (NEURALIZER_SECRET)
    2. Buscar DemoSession por session_id
    3. Llamar a DemoRAGService.cleanup_session_vectors() para limpiar vectores (Quest 2.2)
    4. Marcar sesión como inactive, establecer closed_at
    5. Si save_lead=True, crear registro DemoLead con datos
    6. Retornar NeuralizerResponse con estadística de vectores eliminados
    
    Args:
        request: NeuralizerRequest con session_id, secret_word, save_lead
        db: Sesión de base de datos
        
    Returns:
        NeuralizerResponse confirmando cierre y limpieza
    """
    
    try:
        # Validar palabra secreta
        if request.secret_word != NEURALIZER_SECRET:
            raise HTTPException(
                status_code=403,
                detail="Palabra secreta incorrecta. Acceso denegado."
            )
        
        # Buscar sesión en DB
        demo_session = db.query(DemoSession).filter(
            DemoSession.id == request.session_id
        ).first()
        
        if not demo_session:
            raise HTTPException(
                status_code=404,
                detail=f"Sesion {request.session_id} no encontrada"
            )
        
        # Integración Quest 2.2: Limpiar vectores RAG
        vectors_deleted = 0
        try:
            rag_service = DemoRAGService()
            cleanup_result = rag_service.cleanup_session_vectors(
                session_id=request.session_id,
                db=db
            )
            vectors_deleted = cleanup_result.get("deleted_vectors", 0)
            logger.info(f"RAG cleanup complete: {vectors_deleted} vectors deleted")
        except Exception as e:
            logger.error(f"RAG cleanup failed: {str(e)}")
            # No fallar el reset si la limpieza RAG falla
            vectors_deleted = 0
        
        # Cerrar sesión
        demo_session.active = False
        demo_session.closed_at = datetime.utcnow()
        db.add(demo_session)
        
        lead_saved = False
        
        # Si se solicita guardar lead, crear registro
        if request.save_lead:
            try:
                demo_lead = DemoLead(
                    session_id=demo_session.id,
                    prospect_name="Prospecto Demo",
                    prospect_phone="+34 000 000 000",
                    interest_level="caliente",
                    notes={
                        "business_name": demo_session.business_name,
                        "business_type": demo_session.business_type,
                        "vectors_indexed": vectors_deleted,
                    }
                )
                db.add(demo_lead)
                lead_saved = True
            except Exception as e:
                logger.warning(f"Error guardando lead: {str(e)}")
        
        db.commit()
        
        return NeuralizerResponse(
            session_id=str(demo_session.id),
            status="closed",
            message=f"Sesion de demo cerrada exitosamente. {vectors_deleted} vectores RAG eliminados.",
            lead_saved=lead_saved
        )
    
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error en neuralizer_reset: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error al cerrar sesion: {str(e)}")


# ============================================================================
# HEALTH CHECK
# ============================================================================
@router.get(
    "/health",
    summary="Health check del modulo Demo",
    tags=["Health"],
)
async def demo_health():
    """Verifica que el modulo demo está activo."""
    return {
        "status": "healthy",
        "module": "demo",
        "version": "1.0.0",
    }
