"""
Demo module for commercial demonstration.
Módulo de demostración comercial de SmartOps.
"""

from .models import DemoSession, DemoLead
from .schemas import (
    DemoUploadMetadata,
    NeuralizerRequest,
    NeuralizerResponse,
    DemoSessionResponse,
    MessageRequest,
    MessageResponse,
    DemoSessionCreate,
    DemoLeadCreate,
    DemoSessionDetail,
    DemoLeadDetail,
)

__all__ = [
    "DemoSession",
    "DemoLead",
    "DemoUploadMetadata",
    "NeuralizerRequest",
    "NeuralizerResponse",
    "DemoSessionResponse",
    "MessageRequest",
    "MessageResponse",
    "DemoSessionCreate",
    "DemoLeadCreate",
    "DemoSessionDetail",
    "DemoLeadDetail",
]
