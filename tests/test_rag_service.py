"""
Unit tests para Demo RAG Service.
Verifica indexación, búsqueda y limpieza de vectores.
"""

import pytest
import os
import tempfile
from uuid import uuid4
from unittest.mock import Mock, patch, MagicMock
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import Base
from app.services.demo_rag import DemoRAGService
from app.modules.demo.models import DemoSession, DemoVector


@pytest.fixture
def test_db():
    """Crea BD de prueba."""
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    yield db
    db.close()


@pytest.fixture
def mock_rag_service():
    """Crea DemoRAGService mockeado."""
    with patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"}):
        service = DemoRAGService()
        # Mock del cliente OpenAI
        service.client = Mock()
        return service


class TestDemoRAGServiceInit:
    """Tests de inicialización del servicio RAG."""
    
    def test_rag_service_init_with_key(self):
        """Debe inicializar correctamente con API key."""
        with patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"}):
            service = DemoRAGService()
            assert service.embedding_model == "text-embedding-3-small"
    
    def test_rag_service_init_without_key(self):
        """Debe fallar sin API key."""
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(ValueError):
                DemoRAGService()


class TestChunkingLogic:
    """Tests para la lógica de chunking."""
    
    def test_chunk_text_small(self, mock_rag_service):
        """Debe retornar como un chunk si es pequeño."""
        text = "Este es un texto pequeño"
        chunks = mock_rag_service._chunk_text(text, chunk_size=1000)
        assert len(chunks) == 1
        assert chunks[0] == text
    
    def test_chunk_text_multiple(self, mock_rag_service):
        """Debe dividir texto en múltiples chunks."""
        # Crear texto con párrafos
        text = "\n\n".join([f"Párrafo {i}" * 100 for i in range(5)])
        chunks = mock_rag_service._chunk_text(text, chunk_size=200)
        assert len(chunks) > 1
    
    def test_chunk_text_empty(self, mock_rag_service):
        """Debe retornar lista vacía para texto vacío."""
        chunks = mock_rag_service._chunk_text("", chunk_size=1000)
        assert len(chunks) == 0
    
    def test_chunk_text_respects_size(self, mock_rag_service):
        """Cada chunk debe respetar max_size."""
        text = "\n\n".join([f"Párrafo {i}" * 50 for i in range(10)])
        chunks = mock_rag_service._chunk_text(text, chunk_size=500)
        for chunk in chunks:
            # Algunos pueden ser un poco más grandes debido a overhead
            assert len(chunk) <= 600  # Margen tolerancia


class TestEmbeddingGeneration:
    """Tests para generación de embeddings."""
    
    def test_get_embedding_success(self, mock_rag_service):
        """Debe generar embedding correctamente."""
        # Mock response
        mock_response = Mock()
        mock_response.data = [Mock(embedding=[0.1] * 1536)]
        mock_rag_service.client.embeddings.create.return_value = mock_response
        
        embedding = mock_rag_service._get_embedding("test text")
        assert len(embedding) == 1536
        assert embedding[0] == 0.1
    
    def test_get_embedding_calls_api(self, mock_rag_service):
        """Debe llamar a OpenAI API correctamente."""
        mock_response = Mock()
        mock_response.data = [Mock(embedding=[0.2] * 1536)]
        mock_rag_service.client.embeddings.create.return_value = mock_response
        
        mock_rag_service._get_embedding("test text")
        mock_rag_service.client.embeddings.create.assert_called_once()
        call_args = mock_rag_service.client.embeddings.create.call_args
        assert call_args[1]["model"] == "text-embedding-3-small"
    
    def test_get_embedding_error_handling(self, mock_rag_service):
        """Debe manejar errores de API."""
        mock_rag_service.client.embeddings.create.side_effect = Exception("API Error")
        
        with pytest.raises(RuntimeError):
            mock_rag_service._get_embedding("test text")


class TestPDFExtraction:
    """Tests para extracción de PDF."""
    
    def test_extract_from_nonexistent_pdf(self, mock_rag_service):
        """Debe fallar si PDF no existe."""
        with pytest.raises(FileNotFoundError):
            mock_rag_service._extract_text_from_pdf("/tmp/nonexistent.pdf")
    
    @patch('app.services.demo_rag.PdfReader')
    def test_extract_from_pdf_success(self, mock_pdf_reader, mock_rag_service):
        """Debe extraer texto de PDF."""
        # Mock PDF
        mock_page = Mock()
        mock_page.extract_text.return_value = "Contenido del PDF"
        mock_reader = Mock()
        mock_reader.pages = [mock_page]
        mock_pdf_reader.return_value = mock_reader
        
        # Crear archivo dummy en temp
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as f:
            f.write(b"dummy")
            temp_path = f.name
        
        try:
            text = mock_rag_service._extract_text_from_pdf(temp_path)
            assert "Contenido del PDF" in text
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)


class TestImageExtraction:
    """Tests para extracción de imagen."""
    
    def test_extract_from_nonexistent_image(self, mock_rag_service):
        """Debe fallar si imagen no existe."""
        with pytest.raises(FileNotFoundError):
            mock_rag_service._extract_text_from_image("/tmp/nonexistent.jpg")
    
    def test_extract_from_image_success(self, mock_rag_service):
        """Debe extraer texto de imagen con GPT-4o Vision."""
        # Mock GPT-4o response
        mock_response = Mock()
        mock_response.choices = [Mock(message=Mock(content="Texto de la imagen"))]
        mock_rag_service.client.chat.completions.create.return_value = mock_response
        
        # Crear archivo dummy
        with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as f:
            f.write(b"dummy image")
            temp_path = f.name
        
        try:
            text = mock_rag_service._extract_text_from_image(temp_path)
            assert "Texto de la imagen" in text
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)


class TestIndexing:
    """Tests para indexación de documentos."""
    
    def test_index_demo_document_structure(self, mock_rag_service, test_db):
        """Debe retornar estructura correcta después de indexar."""
        session_id = uuid4()
        
        # Setup mocks
        mock_rag_service._extract_text_from_pdf = Mock(return_value="Texto del documento " * 100)
        mock_rag_service._chunk_text = Mock(return_value=["Chunk 1", "Chunk 2"])
        mock_rag_service._get_embedding = Mock(return_value=[0.1] * 1536)
        
        # Crear sesión
        demo_session = DemoSession(
            id=session_id,
            business_type="restaurante",
            business_name="Test"
        )
        test_db.add(demo_session)
        test_db.commit()
        
        # Mock del archivo
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as f:
            f.write(b"dummy")
            temp_path = f.name
        
        try:
            result = mock_rag_service.index_demo_document(
                session_id=session_id,
                file_path=temp_path,
                db=test_db
            )
            
            assert result["status"] == "indexed"
            assert result["chunks"] == 2
            assert "session_id" in result
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)
    
    def test_index_creates_vectors_in_db(self, mock_rag_service, test_db):
        """Debe crear vectores en la BD."""
        session_id = uuid4()
        
        # Setup
        mock_rag_service._extract_text_from_pdf = Mock(return_value="Test " * 500)
        mock_rag_service._chunk_text = Mock(return_value=["Chunk A", "Chunk B", "Chunk C"])
        mock_rag_service._get_embedding = Mock(return_value=[0.1] * 1536)
        
        demo_session = DemoSession(
            id=session_id,
            business_type="restaurante",
            business_name="Test"
        )
        test_db.add(demo_session)
        test_db.commit()
        
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as f:
            f.write(b"dummy")
            temp_path = f.name
        
        try:
            mock_rag_service.index_demo_document(
                session_id=session_id,
                file_path=temp_path,
                db=test_db
            )
            
            # Verificar vectores en BD
            vectors = test_db.query(DemoVector).filter_by(session_id=session_id).all()
            assert len(vectors) == 3
            assert vectors[0].chunk_number == 1
            assert vectors[1].chunk_number == 2
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)


class TestSearch:
    """Tests para búsqueda vectorial."""
    
    @pytest.mark.skip(reason="pgvector <=> operator only works with PostgreSQL, not SQLite")
    def test_query_demo_returns_context(self, mock_rag_service, test_db):
        """Debe retornar contexto de búsqueda (skip en SQLite, funciona en PG)."""
        session_id = uuid4()
        
        # Crear sesión y vectores
        demo_session = DemoSession(
            id=session_id,
            business_type="restaurante",
            business_name="Test"
        )
        test_db.add(demo_session)
        
        for i in range(3):
            vector = DemoVector(
                id=uuid4(),
                session_id=session_id,
                chunk_number=i + 1,
                chunk_text=f"Información del menú {i}",
                embedding=[0.1 + i*0.1] * 1536
            )
            test_db.add(vector)
        test_db.commit()
        
        # Mock embedding
        mock_rag_service._get_embedding = Mock(return_value=[0.1] * 1536)
        
        # Query
        context = mock_rag_service.query_demo(
            session_id=session_id,
            question="¿Cuál es el menú?",
            db=test_db
        )
        
        assert "Información del menú" in context
        assert "[Chunk" in context


class TestCleanup:
    """Tests para limpieza de vectores."""
    
    def test_cleanup_deletes_vectors(self, mock_rag_service, test_db):
        """Debe eliminar vectores de sesión."""
        session_id = uuid4()
        
        # Crear vectores
        demo_session = DemoSession(
            id=session_id,
            business_type="restaurante",
            business_name="Test"
        )
        test_db.add(demo_session)
        
        for i in range(5):
            vector = DemoVector(
                id=uuid4(),
                session_id=session_id,
                chunk_number=i + 1,
                chunk_text=f"Chunk {i}",
                embedding=[0.1] * 1536
            )
            test_db.add(vector)
        test_db.commit()
        
        # Verificar que existen
        assert test_db.query(DemoVector).filter_by(session_id=session_id).count() == 5
        
        # Cleanup
        result = mock_rag_service.cleanup_session_vectors(
            session_id=session_id,
            db=test_db
        )
        
        assert result["deleted_vectors"] == 5
        assert result["status"] == "cleaned"
        assert test_db.query(DemoVector).filter_by(session_id=session_id).count() == 0
    
    def test_cleanup_nothing_to_clean(self, mock_rag_service, test_db):
        """Debe manejar cleanup sin vectores."""
        session_id = uuid4()
        
        result = mock_rag_service.cleanup_session_vectors(
            session_id=session_id,
            db=test_db
        )
        
        assert result["deleted_vectors"] == 0
        assert result["status"] == "nothing_to_clean"
