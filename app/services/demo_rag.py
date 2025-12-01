"""
Demo RAG Service (Quest 2.2)
============================
Servicio de Retrieval-Augmented Generation para Demo Comercial.
Implementa el contrato RAG: indexación, búsqueda y limpieza de vectores.

Real Implementation:
- index_demo_document(): PDF ingestion con pypdf + OpenAI embeddings
- query_demo(): Búsqueda vectorial con pgvector similarity search
- cleanup_session_vectors(): Eliminación de vectores en pgvector

Dependencies:
- pypdf: PDF text extraction
- openai: Embedding generation (text-embedding-3-small)
- pgvector: PostgreSQL vector similarity
"""

import os
from typing import Dict, List, Optional
import logging
from sqlalchemy.orm import Session
from sqlalchemy import and_, delete
import base64

from app.modules.demo.constants import (
    DEMO_RAG_CATEGORY,
    DEMO_INDEX_PREFIX,
    MAX_CHUNK_SIZE,
)
from app.modules.demo.models import DemoVector

logger = logging.getLogger(__name__)

try:
    from pypdf import PdfReader
except ImportError:
    logger.error("pypdf not installed. Run: pip install pypdf")
    PdfReader = None

try:
    from openai import OpenAI
except ImportError:
    logger.error("openai not installed. Run: pip install openai")
    OpenAI = None


class DemoRAGService:
    """
    Gestor de RAG para la Demo Comercial.
    Aísla toda la lógica de vectores, indexación y búsqueda.
    """

    def __init__(self):
        """Inicializa el servicio con cliente OpenAI."""
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable not set")
        self.client = OpenAI(api_key=api_key)
        self.embedding_model = "text-embedding-3-small"

    def _get_embedding(self, text: str) -> List[float]:
        """
        Genera embedding para un texto usando OpenAI API.
        
        Args:
            text (str): Texto a embeddear.
            
        Returns:
            List[float]: Vector de 1536 dimensiones.
            
        Raises:
            RuntimeError: Si la API falla.
        """
        try:
            response = self.client.embeddings.create(
                input=text,
                model=self.embedding_model
            )
            return response.data[0].embedding
        except Exception as e:
            logger.error(f"Error generating embedding: {e}")
            raise RuntimeError(f"OpenAI API error: {str(e)}")

    def _extract_text_from_pdf(self, file_path: str) -> str:
        """
        Extrae texto de un archivo PDF usando pypdf.
        
        Args:
            file_path (str): Ruta al archivo PDF.
            
        Returns:
            str: Texto completo del PDF.
            
        Raises:
            FileNotFoundError: Si el archivo no existe.
            ValueError: Si el PDF es ilegible.
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"PDF file not found: {file_path}")
        
        try:
            reader = PdfReader(file_path)
            text = ""
            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
            
            if not text.strip():
                raise ValueError("PDF appears to be empty or unreadable")
            
            return text
        except Exception as e:
            logger.error(f"Error reading PDF: {e}")
            raise ValueError(f"Failed to read PDF: {str(e)}")

    def _extract_text_from_image(self, file_path: str) -> str:
        """
        Extrae texto de una imagen (JPG/PNG) usando GPT-4o Vision.
        
        Útil para menús, documentos escaneados, pizarras, etc.
        
        Args:
            file_path (str): Ruta al archivo de imagen (JPG/PNG).
            
        Returns:
            str: Texto extraído de la imagen mediante Vision API.
            
        Raises:
            FileNotFoundError: Si el archivo no existe.
            ValueError: Si la imagen no se puede procesar.
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Image file not found: {file_path}")
        
        try:
            # Paso 1: Leer archivo y convertir a base64
            with open(file_path, "rb") as f:
                image_data = f.read()
            image_base64 = base64.standard_b64encode(image_data).decode("utf-8")
            
            # Determinare MIME type basado en extensión
            file_ext = os.path.splitext(file_path)[1].lower()
            mime_type = "image/jpeg" if file_ext in [".jpg", ".jpeg"] else "image/png"
            
            # Paso 2: Llamar a GPT-4o Vision API
            logger.debug(f"Calling GPT-4o Vision API for {file_path}")
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:{mime_type};base64,{image_base64}"
                                },
                            },
                            {
                                "type": "text",
                                "text": (
                                    "Transcribe todo el texto visible en esta imagen de forma estructurada. "
                                    "Si es un menú, lista todos los platos con sus precios. "
                                    "Si es un documento, preserva la estructura y formato. "
                                    "Si hay tablas, conviértelas a formato legible. "
                                    "Retorna solo el texto extraído, sin comentarios adicionales."
                                ),
                            },
                        ],
                    }
                ],
                max_tokens=4096,
            )
            
            extracted_text = response.choices[0].message.content
            if not extracted_text or not extracted_text.strip():
                raise ValueError("GPT-4o returned empty response for image")
            
            logger.info(f"Successfully extracted {len(extracted_text)} characters from image")
            return extracted_text
            
        except Exception as e:
            logger.error(f"Error extracting text from image: {e}")
            raise ValueError(f"Failed to process image with GPT-4o: {str(e)}")


    def _chunk_text(self, text: str, chunk_size: int = MAX_CHUNK_SIZE) -> List[str]:
        """
        Divide texto en chunks de tamaño máximo.
        Intenta respetar límites naturales (párrafos, oraciones).
        
        Args:
            text (str): Texto a dividir.
            chunk_size (int): Tamaño máximo de cada chunk.
            
        Returns:
            List[str]: Lista de chunks.
        """
        chunks = []
        
        # Si el texto es más pequeño que el chunk_size, retorna como único chunk
        if len(text) <= chunk_size:
            return [text.strip()] if text.strip() else []
        
        # Divide por párrafos primero
        paragraphs = text.split("\n\n")
        current_chunk = ""
        
        for paragraph in paragraphs:
            paragraph = paragraph.strip()
            if not paragraph:
                continue
            
            # Si agregar este párrafo excede el limite
            if len(current_chunk) + len(paragraph) + 2 > chunk_size:
                # Si el chunk actual tiene contenido, guárdalo
                if current_chunk.strip():
                    chunks.append(current_chunk.strip())
                current_chunk = paragraph
            else:
                # Agrega el párrafo al chunk actual
                if current_chunk:
                    current_chunk += "\n\n" + paragraph
                else:
                    current_chunk = paragraph
        
        # No olvides el último chunk
        if current_chunk.strip():
            chunks.append(current_chunk.strip())
        
        return chunks

    def index_demo_document(
        self, session_id: str, file_path: str, db: Session
    ) -> Dict[str, any]:
        """
        Ingesta de documento PDF o Imagen para la Demo.

        Procesa el archivo detectando su tipo:
        - PDF: Extrae texto con pypdf
        - Imagen (JPG/PNG): Extrae texto con GPT-4o Vision
        
        Luego divide en chunks, genera embeddings con OpenAI,
        e indexa bajo la categoría DEMO_RAG_CATEGORY.

        Args:
            session_id (str): UUID de la sesión demo.
            file_path (str): Ruta local al archivo (PDF o Imagen).
            db (Session): Sesión de base de datos SQLAlchemy.

        Returns:
            dict: Estructura {
                'chunks': int (cantidad de chunks generados),
                'status': str ('indexed'),
                'category': str (DEMO_RAG_CATEGORY),
                'session_id': str (UUID de sesión),
                'file_type': str ('pdf' o 'image'),
            }

        Raises:
            FileNotFoundError: Si el archivo no existe.
            ValueError: Si el archivo está vacío o no se puede procesar.
            RuntimeError: Si OpenAI falla.
        """
        try:
            logger.info(f"Starting document indexing for session {session_id}")
            
            # Paso 1: Detectar tipo de archivo y extraer texto
            file_ext = os.path.splitext(file_path)[1].lower()
            file_type = "pdf" if file_ext == ".pdf" else "image"
            
            if file_type == "pdf":
                logger.debug("Processing as PDF")
                document_text = self._extract_text_from_pdf(file_path)
            else:
                logger.debug(f"Processing as image ({file_ext})")
                document_text = self._extract_text_from_image(file_path)
            
            logger.info(f"Extracted {len(document_text)} characters from {file_type}")
            
            # Paso 2: Dividir en chunks
            chunks = self._chunk_text(document_text)
            logger.info(f"Generated {len(chunks)} chunks from {file_type}")
            
            if not chunks:
                raise ValueError("No chunks generated from document")
            
            # Paso 3: Generar embeddings y guardar en DB
            demo_vectors = []
            for chunk_num, chunk_text in enumerate(chunks, start=1):
                logger.debug(f"Processing chunk {chunk_num}/{len(chunks)}")
                
                # Generar embedding
                embedding = self._get_embedding(chunk_text)
                
                # Crear objeto DemoVector
                demo_vector = DemoVector(
                    session_id=session_id,
                    chunk_number=chunk_num,
                    chunk_text=chunk_text,
                    embedding=embedding,
                    chunk_metadata={
                        "category": DEMO_RAG_CATEGORY,
                        "file_type": file_type,
                        "chunk_size": len(chunk_text),
                        "index_prefix": DEMO_INDEX_PREFIX,
                    }
                )
                demo_vectors.append(demo_vector)
            
            # Paso 4: Guardar todos los vectores en la DB
            db.add_all(demo_vectors)
            db.commit()
            logger.info(f"Successfully indexed {len(chunks)} chunks from {file_type} for session {session_id}")
            
            return {
                "chunks": len(chunks),
                "status": "indexed",
                "category": DEMO_RAG_CATEGORY,
                "session_id": str(session_id),
                "file_path": file_path,
                "file_type": file_type,
                "message": f"Successfully indexed {len(chunks)} chunks from {file_type.upper()}"
            }
            
        except Exception as e:
            db.rollback()
            logger.error(f"Error indexing document: {e}")
            raise

    def query_demo(self, session_id: str, question: str, db: Session) -> str:
        """
        Búsqueda vectorial en la Demo.

        Convierte la pregunta a embedding, busca similares en los vectores
        indexados, filtra por session_id y DEMO_RAG_CATEGORY,
        y retorna los chunks más relevantes.

        Args:
            session_id (str): UUID de la sesión demo.
            question (str): Pregunta del usuario.
            db (Session): Sesión de base de datos SQLAlchemy.

        Returns:
            str: Texto concatenado de los 3 chunks más similares.

        Raises:
            ValueError: Si session_id no existe en DB.
            RuntimeError: Si el índice está vacío o la búsqueda falla.

        Note:
            Usa pgvector <-> operator para similarity search.
        """
        try:
            logger.info(f"Querying RAG for session {session_id}: {question[:50]}...")
            
            # Paso 1: Generar embedding de la pregunta
            question_embedding = self._get_embedding(question)
            
            # Paso 2: Buscar vectores similares en pgvector
            # Nota: Usando <-> operator (cosine distance) en pgvector
            similar_vectors = (
                db.query(DemoVector)
                .filter(DemoVector.session_id == session_id)
                .order_by(DemoVector.embedding.cosine_distance(question_embedding))
                .limit(3)
                .all()
            )
            
            if not similar_vectors:
                logger.warning(f"No vectors found for session {session_id}")
                return "No relevant context found in the indexed document."
            
            # Paso 3: Concatenar chunks más relevantes
            context = "\n\n---\n\n".join(
                [f"[Chunk {v.chunk_number}]\n{v.chunk_text}" for v in similar_vectors]
            )
            
            logger.info(f"Found {len(similar_vectors)} relevant chunks")
            return context
            
        except Exception as e:
            logger.error(f"Error querying RAG: {e}")
            raise RuntimeError(f"RAG query failed: {str(e)}")

    def cleanup_session_vectors(self, session_id: str, db: Session) -> Dict[str, any]:
        """
        Limpieza de vectores asociados a sesión (Neuralizer).

        Borra todos los embeddings, chunks indexados y metadata
        asociados a esta sesión en la categoría DEMO_RAG_CATEGORY.

        Args:
            session_id (str): UUID de la sesión demo a limpiar.
            db (Session): Sesión de base de datos SQLAlchemy.

        Returns:
            dict: Estructura {
                'deleted_vectors': int (cantidad de vectores eliminados),
                'status': str ('cleaned' o 'nothing_to_clean'),
                'session_id': str (UUID),
            }

        Raises:
            ValueError: Si session_id no existe en DB.
        """
        try:
            logger.info(f"Cleaning vectors for session {session_id}")
            
            # Contar vectores a eliminar
            count = db.query(DemoVector).filter(
                DemoVector.session_id == session_id
            ).count()
            
            # Eliminar
            db.query(DemoVector).filter(
                DemoVector.session_id == session_id
            ).delete()
            db.commit()
            
            status = "cleaned" if count > 0 else "nothing_to_clean"
            logger.info(f"Cleaned {count} vectors for session {session_id}")
            
            return {
                "deleted_vectors": count,
                "status": status,
                "session_id": str(session_id),
                "message": f"Deleted {count} vectors from session"
            }
            
        except Exception as e:
            db.rollback()
            logger.error(f"Error cleaning vectors: {e}")
            raise

    def get_index_prefix(self) -> str:
        """Retorna el prefijo estándar para índices de demo."""
        return DEMO_INDEX_PREFIX

    def get_category(self) -> str:
        """Retorna la categoría reservada para demo."""
        return DEMO_RAG_CATEGORY

    def get_max_chunk_size(self) -> int:
        """Retorna el tamaño máximo de chunks."""
        return MAX_CHUNK_SIZE

