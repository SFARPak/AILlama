"""
AIllama - A complete Python implementation of Ollama
"""

__version__ = "0.1.0"
__author__ = "AI Assistant"
__description__ = "A complete Python implementation of Ollama for running large language models locally"

from .core import AIllama
from .model_manager import ModelManager
from .inference_engine import InferenceEngine
from .types import ModelInfo, GenerateResponse, ChatResponse, ChatMessage

__all__ = ["AIllama", "ModelManager", "InferenceEngine", "ModelInfo", "GenerateResponse", "ChatResponse", "ChatMessage"]
