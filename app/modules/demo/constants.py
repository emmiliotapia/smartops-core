"""
Demo Module Constants
=====================
Constantes reservadas para la Demo Comercial (Quest 2.1).
Define los parámetros globales para el RAG integration.

Categories:
    - DEMO_RAG_CATEGORY: Categoría reservada para indexación de documentos demo
    - DEMO_INDEX_PREFIX: Prefijo usado en todos los índices de demo
    - MAX_CHUNK_SIZE: Tamaño máximo de chunks para procesamiento de PDFs
"""

# RAG Configuration
DEMO_RAG_CATEGORY = "demo_comercial"
DEMO_INDEX_PREFIX = "demo_v1"

# PDF Processing
MAX_CHUNK_SIZE = 1000  # caracteres por chunk

# Session Management
DEMO_SESSION_TIMEOUT_MINUTES = 30  # Duración máxima de sesión demo
DEMO_NEURALIZER_SECRET = "neuralizer"  # Palabra clave para resetear sesión
