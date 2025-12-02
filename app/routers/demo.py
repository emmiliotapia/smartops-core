"""
Router for Demo module endpoints.

Implements 3 main endpoints:
- POST /demo/upload: THE LOADER - Document ingestion with RAG indexing
- POST /demo/message: THE SHOW - Semantic search with RAG retrieval
- POST /demo/reset: THE NEURALIZER - Session cleanup and vector deletion
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
    tags=["demo"],
)

# Security configuration
NEURALIZER_SECRET = os.getenv("NEURALIZER_SECRET", "flash")
UPLOAD_DIR = "/tmp/smartops_demo_uploads"


# Utilities
def ensure_upload_dir():
    """Create upload directory if it does not exist."""
    os.makedirs(UPLOAD_DIR, exist_ok=True)


# ============================================================================
# ENDPOINT 1: THE LOADER - POST /demo/upload
# ============================================================================
@router.post(
    "/upload",
    response_model=DemoSessionResponse,
    summary="Upload document for demo",
    description="Create demo session with PDF/image file and business metadata.",
)
async def upload_demo(
    file: UploadFile = File(...),
    business_name: str = Form(...),
    business_type: str = Form(...),
    db: Session = Depends(get_db),
):
    """
    THE LOADER - Document ingestion endpoint.

    Workflow:
    1. Validate file type (PDF or image)
    2. Create DemoSession in database
    3. Save file to disk
    4. Call DemoRAGService.index_demo_document() for RAG indexing
    5. Return session_id with chunk indexing statistics

    Args:
        file: File to process (PDF or image)
        business_name: Business name
        business_type: Business type (restaurant, clinic, etc)
        db: Database session

    Returns:
        DemoSessionResponse with session_id and chunks_indexed
    """

    try:
        # Validate file type (PDF + Images for Vision)
        allowed_types = {"application/pdf", "image/jpeg", "image/png"}
        content_type = file.content_type or ""

        # Map content-type to file extension
        type_to_ext = {
            "application/pdf": ".pdf",
            "image/jpeg": ".jpg",
            "image/png": ".png"
        }

        if content_type not in allowed_types:
            raise HTTPException(
                status_code=400,
                detail=f"File type not allowed. Allowed: PDF, JPEG, PNG. Received: {content_type}"
            )

        file_extension = type_to_ext.get(content_type, ".bin")

        # Create DemoSession record in DB
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

        # Save file to disk
        ensure_upload_dir()
        file_path = f"{UPLOAD_DIR}/{session_id}{file_extension}"
        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)

        # RAG indexing: Index PDF with semantic search
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
            # Do not fail upload if RAG fails, but log error
            logger.error(f"RAG indexing failed: {str(e)}")
            chunks_indexed = 0
            rag_status = "failed"
            rag_message = f"RAG indexing failed: {str(e)}"

        return DemoSessionResponse(
            session_id=str(demo_session.id),
            status="active",
            message=f"Demo session started for {business_name} ({business_type}). {rag_message}"
        )

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error in upload_demo: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error creating session: {str(e)}")


# ============================================================================
# ENDPOINT 2: THE SHOW - POST /demo/message
# ============================================================================
@router.post(
    "/message",
    response_model=MessageResponse,
    summary="Chat with demo bot",
    description="Send message to demo and receive context-aware response from RAG.",
)
async def send_message(
    request: MessageRequest,
    db: Session = Depends(get_db),
):
    """
    THE SHOW - Bot interaction endpoint.

    Workflow:
    1. Find DemoSession by session_id
    2. Validate existence and active status
    3. Call DemoRAGService.query_demo() for vector semantic search
    4. Return context-aware response with most relevant chunks

    Args:
        request: MessageRequest with session_id and message
        db: Database session

    Returns:
        MessageResponse with bot response (RAG context)
    """

    try:
        # Convert session_id string to UUID for queries
        try:
            session_uuid = uuid.UUID(request.session_id)
        except (ValueError, TypeError):
            raise HTTPException(status_code=400, detail="Invalid session_id")

        # Find session in DB
        demo_session = db.query(DemoSession).filter(
            DemoSession.id == session_uuid
        ).first()

        if not demo_session:
            raise HTTPException(
                status_code=404,
                detail=f"Session {request.session_id} not found"
            )

        if not demo_session.active:
            raise HTTPException(
                status_code=400,
                detail="Demo session has been closed"
            )

        # RAG retrieval: Search context
        bot_response = ""
        try:
            rag_service = DemoRAGService()
            # Vector semantic search
            context = rag_service.query_demo(
                session_id=request.session_id,
                question=request.message,
                db=db
            )
            # In production, LLM would generate response with context
            # For now, return RAG context directly
            bot_response = f"Found context:\n\n{context}"
            logger.info(f"RAG query executed for session {request.session_id}")
        except Exception as e:
            logger.error(f"RAG query failed: {str(e)}")
            # Fallback to error response if RAG fails
            bot_response = f"Sorry, could not retrieve document context: {str(e)}"

        return MessageResponse(
            session_id=str(demo_session.id),
            response=bot_response,
            business_type=demo_session.business_type
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in send_message: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error processing message: {str(e)}")


# ============================================================================
# ENDPOINT 3: THE NEURALIZER - POST /demo/reset
# ============================================================================
@router.post(
    "/reset",
    response_model=NeuralizerResponse,
    summary="Close and cleanup demo session",
    description="Close demo session, validate secret word, cleanup RAG vectors, and optionally save lead.",
)
async def neuralizer_reset(
    request: NeuralizerRequest,
    db: Session = Depends(get_db),
):
    """
    THE NEURALIZER - Session cleanup endpoint.

    Workflow:
    1. Validate secret word (NEURALIZER_SECRET)
    2. Find DemoSession by session_id
    3. Call DemoRAGService.cleanup_session_vectors() to cleanup vectors
    4. Mark session as inactive, set closed_at timestamp
    5. If save_lead=True, create DemoLead record with data
    6. Return NeuralizerResponse with vector deletion statistics

    Args:
        request: NeuralizerRequest with session_id, secret_word, save_lead
        db: Database session

    Returns:
        NeuralizerResponse confirming closure and cleanup
    """

    try:
        # Validate secret word
        if request.secret_word != NEURALIZER_SECRET:
            raise HTTPException(
                status_code=403,
                detail="Incorrect secret word. Access denied."
            )

        # Convert session_id string to UUID for queries
        try:
            session_uuid = uuid.UUID(request.session_id)
        except (ValueError, TypeError):
            raise HTTPException(status_code=400, detail="Invalid session_id")

        # Find session in DB
        demo_session = db.query(DemoSession).filter(
            DemoSession.id == session_uuid
        ).first()

        if not demo_session:
            raise HTTPException(
                status_code=404,
                detail=f"Session {request.session_id} not found"
            )

        # RAG cleanup: Delete vectors
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
            # Do not fail reset if RAG cleanup fails
            vectors_deleted = 0

        # Close session
        demo_session.active = False
        demo_session.closed_at = datetime.utcnow()
        db.add(demo_session)

        lead_saved = False

        # If requested, save lead record
        if request.save_lead:
            try:
                demo_lead = DemoLead(
                    session_id=demo_session.id,
                    prospect_name="Demo Prospect",
                    prospect_phone="+34 000 000 000",
                    interest_level="hot",
                    notes={
                        "business_name": demo_session.business_name,
                        "business_type": demo_session.business_type,
                        "vectors_indexed": vectors_deleted,
                    }
                )
                db.add(demo_lead)
                lead_saved = True
            except Exception as e:
                logger.warning(f"Error saving lead: {str(e)}")

        db.commit()

        return NeuralizerResponse(
            session_id=str(demo_session.id),
            status="closed",
            message=f"Demo session closed successfully. {vectors_deleted} RAG vectors deleted.",
            lead_saved=lead_saved
        )

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error in neuralizer_reset: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error closing session: {str(e)}")


# ============================================================================
# HEALTH CHECK
# ============================================================================
@router.get(
    "/health",
    summary="Health check for demo module",
    tags=["health"],
)
async def demo_health():
    """Check that demo module is active."""
    return {
        "status": "healthy",
        "module": "demo",
        "version": "1.0.0",
    }
