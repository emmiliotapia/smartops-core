"""
Demo RAG Service

Retrieval-Augmented Generation service for commercial demo.
Implements RAG contract: document indexing, semantic search, vector cleanup.

Real Implementation:
- index_demo_document(): PDF/Image ingestion with pypdf + OpenAI embeddings
- query_demo(): Vector similarity search with pgvector
- cleanup_session_vectors(): Vector deletion with pgvector

Dependencies:
- pypdf: PDF text extraction
- openai: Embedding generation (text-embedding-3-small) + Vision API
- pgvector: PostgreSQL vector similarity search
"""

import os
from typing import Dict, List, Optional, Any
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
    RAG manager for commercial demo.
    Encapsulates all vector indexing, retrieval, and cleanup logic.
    """

    def __init__(self):
        """Initialize service with OpenAI client."""
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable not set")
        self.client = OpenAI(api_key=api_key)
        self.embedding_model = "text-embedding-3-small"

    def _get_embedding(self, text: str) -> List[float]:
        """
        Generate embedding for text using OpenAI API.

        Args:
            text: Text to embed.

        Returns:
            Vector of 1536 dimensions.

        Raises:
            RuntimeError: If API call fails.
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
        Extract text from PDF file using pypdf.

        Args:
            file_path: Path to PDF file.

        Returns:
            Complete text from PDF.

        Raises:
            FileNotFoundError: If file does not exist.
            ValueError: If PDF is unreadable.
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
        Extract text from image (JPG/PNG) using GPT-4o Vision.

        Useful for menus, scanned documents, whiteboards, etc.

        Args:
            file_path: Path to image file (JPG/PNG).

        Returns:
            Text extracted from image via Vision API.

        Raises:
            FileNotFoundError: If file does not exist.
            ValueError: If image cannot be processed.
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Image file not found: {file_path}")

        try:
            # Step 1: Read file and convert to base64
            with open(file_path, "rb") as f:
                image_data = f.read()
            image_base64 = base64.standard_b64encode(image_data).decode("utf-8")

            # Determine MIME type based on extension
            file_ext = os.path.splitext(file_path)[1].lower()
            mime_type = "image/jpeg" if file_ext in [".jpg", ".jpeg"] else "image/png"

            # Step 2: Call GPT-4o Vision API
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
                                    "Transcribe all visible text in this image in structured format. "
                                    "If it is a menu, list all dishes with prices. "
                                    "If it is a document, preserve structure and formatting. "
                                    "If there are tables, convert to readable format. "
                                    "Return only extracted text, without additional comments."
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
        Divide text into chunks of maximum size.
        Attempts to respect natural boundaries (paragraphs, sentences).

        Args:
            text: Text to divide.
            chunk_size: Maximum size of each chunk.

        Returns:
            List of text chunks.
        """
        chunks = []

        # If text is smaller than chunk_size, return as single chunk
        if len(text) <= chunk_size:
            return [text.strip()] if text.strip() else []

        # Split by paragraphs first
        paragraphs = text.split("\n\n")
        current_chunk = ""

        for paragraph in paragraphs:
            paragraph = paragraph.strip()
            if not paragraph:
                continue

            # If adding this paragraph exceeds limit
            if len(current_chunk) + len(paragraph) + 2 > chunk_size:
                # If current chunk has content, save it
                if current_chunk.strip():
                    chunks.append(current_chunk.strip())
                current_chunk = paragraph
            else:
                # Add paragraph to current chunk
                if current_chunk:
                    current_chunk += "\n\n" + paragraph
                else:
                    current_chunk = paragraph

        # Don't forget the last chunk
        if current_chunk.strip():
            chunks.append(current_chunk.strip())

        return chunks

    def index_demo_document(
        self, session_id: str, file_path: str, db: Session
    ) -> Dict[str, Any]:
        """
        Index PDF or image document for demo.

        Processes file by detecting its type:
        - PDF: Extract text with pypdf
        - Image (JPG/PNG): Extract text with GPT-4o Vision

        Then splits into chunks, generates embeddings with OpenAI,
        and indexes under DEMO_RAG_CATEGORY.

        Args:
            session_id: Session UUID.
            file_path: Local path to file (PDF or Image).
            db: SQLAlchemy database session.

        Returns:
            dict: Structure {
                'chunks': int (number of chunks generated),
                'status': str ('indexed'),
                'category': str (DEMO_RAG_CATEGORY),
                'session_id': str (session UUID),
                'file_type': str ('pdf' or 'image'),
            }

        Raises:
            FileNotFoundError: If file does not exist.
            ValueError: If file is empty or cannot be processed.
            RuntimeError: If OpenAI fails.
        """
        try:
            logger.info(f"Starting document indexing for session {session_id}")

            # Step 1: Detect file type and extract text
            file_ext = os.path.splitext(file_path)[1].lower()
            file_type = "pdf" if file_ext == ".pdf" else "image"

            if file_type == "pdf":
                logger.debug("Processing as PDF")
                document_text = self._extract_text_from_pdf(file_path)
            else:
                logger.debug(f"Processing as image ({file_ext})")
                document_text = self._extract_text_from_image(file_path)

            logger.info(f"Extracted {len(document_text)} characters from {file_type}")

            # Step 2: Split into chunks
            chunks = self._chunk_text(document_text)
            logger.info(f"Generated {len(chunks)} chunks from {file_type}")

            if not chunks:
                raise ValueError("No chunks generated from document")

            # Step 3: Generate embeddings and save to DB
            demo_vectors = []
            for chunk_num, chunk_text in enumerate(chunks, start=1):
                logger.debug(f"Processing chunk {chunk_num}/{len(chunks)}")

                # Generate embedding
                embedding = self._get_embedding(chunk_text)

                # Create DemoVector object
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

            # Step 4: Save all vectors to DB
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
        Semantic search on indexed demo vectors.

        Converts question to embedding, searches for similar vectors
        indexed for this session, and returns most relevant chunks.

        Args:
            session_id: Session UUID.
            question: User question.
            db: SQLAlchemy database session.

        Returns:
            Concatenated text of 3 most similar chunks.

        Raises:
            ValueError: If session_id does not exist in DB.
            RuntimeError: If index is empty or search fails.

        Note:
            Uses pgvector <-> operator for cosine distance similarity search.
        """
        try:
            logger.info(f"Querying RAG for session {session_id}: {question[:50]}...")

            # Step 1: Generate embedding for question
            question_embedding = self._get_embedding(question)

            # Step 2: Search for similar vectors using pgvector
            # Note: Using <-> operator (cosine distance) in pgvector
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

            # Step 3: Concatenate most relevant chunks
            context = "\n\n---\n\n".join(
                [f"[Chunk {v.chunk_number}]\n{v.chunk_text}" for v in similar_vectors]
            )

            logger.info(f"Found {len(similar_vectors)} relevant chunks")
            return context

        except Exception as e:
            logger.error(f"Error querying RAG: {e}")
            raise RuntimeError(f"RAG query failed: {str(e)}")

    def cleanup_session_vectors(self, session_id: str, db: Session) -> Dict[str, Any]:
        """
        Cleanup vectors for session (Neuralizer).

        Deletes all embeddings, indexed chunks, and metadata
        associated with this session.

        Args:
            session_id: Session UUID to clean.
            db: SQLAlchemy database session.

        Returns:
            dict: Structure {
                'deleted_vectors': int (number of deleted vectors),
                'status': str ('cleaned' or 'nothing_to_clean'),
                'session_id': str (session UUID),
            }

        Raises:
            ValueError: If session_id does not exist in DB.
        """
        try:
            logger.info(f"Cleaning vectors for session {session_id}")

            # Count vectors to delete
            count = db.query(DemoVector).filter(
                DemoVector.session_id == session_id
            ).count()

            # Delete
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
        """Get standard prefix for demo indexes."""
        return DEMO_INDEX_PREFIX

    def get_category(self) -> str:
        """Get reserved category for demo vectors."""
        return DEMO_RAG_CATEGORY

    def get_max_chunk_size(self) -> int:
        """Get maximum chunk size."""
        return MAX_CHUNK_SIZE
