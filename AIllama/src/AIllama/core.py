import os
import json
from pathlib import Path
from typing import List, Dict, Optional, Any, Union
from dataclasses import dataclass
import logging

from .model_manager import ModelManager
from .inference_engine import InferenceEngine
from .config import Config

logger = logging.getLogger(__name__)


@dataclass
class ModelInfo:
    name: str
    size: int
    path: str
    modified_at: str
    format: str
    parameters: Optional[Dict[str, Any]] = None


@dataclass
class GenerateResponse:
    response: str
    done: bool
    context: Optional[List[int]] = None
    total_duration: Optional[int] = None
    load_duration: Optional[int] = None
    prompt_eval_count: Optional[int] = None
    eval_count: Optional[int] = None
    eval_duration: Optional[int] = None


@dataclass
class ChatMessage:
    role: str
    content: str


@dataclass
class ChatResponse:
    message: ChatMessage
    done: bool
    total_duration: Optional[int] = None
    load_duration: Optional[int] = None
    prompt_eval_count: Optional[int] = None
    eval_count: Optional[int] = None
    eval_duration: Optional[int] = None


class AIllama:
    """Main AIllama class providing Ollama-compatible API"""

    def __init__(self, model_dir: Optional[str] = None, host: str = "localhost", port: int = 11434):
        self.config = Config()
        if model_dir:
            self.config.model_dir = Path(model_dir)
        self.config.host = host
        self.config.port = port

        self.model_manager = ModelManager(self.config)
        self.inference_engine = InferenceEngine(self.config)

        # Setup logging
        logging.basicConfig(level=logging.INFO)

    def list_models(self) -> List[ModelInfo]:
        """List all available models"""
        return self.model_manager.list_models()

    def pull_model(self, model_name: str, force: bool = False) -> None:
        """Download a model from Hugging Face"""
        self.model_manager.pull_model(model_name, force)

    def delete_model(self, model_name: str) -> None:
        """Delete a model"""
        self.model_manager.delete_model(model_name)

    def show_model(self, model_name: str) -> ModelInfo:
        """Show model information"""
        return self.model_manager.get_model_info(model_name)

    def generate(self, model: str, prompt: str, **kwargs) -> GenerateResponse:
        """Generate text from a model"""
        return self.inference_engine.generate(model, prompt, **kwargs)

    def chat(self, model: str, messages: List[Dict[str, str]], **kwargs) -> ChatResponse:
        """Chat with a model"""
        return self.inference_engine.chat(model, messages, **kwargs)

    def embed(self, model: str, input_text: Union[str, List[str]]) -> List[float]:
        """Generate embeddings for text"""
        return self.inference_engine.embed(model, input_text)

    def create_model(self, name: str, modelfile: str) -> None:
        """Create a custom model from a Modelfile"""
        # This would parse the Modelfile and create a custom model
        # For now, just raise NotImplementedError
        raise NotImplementedError("Custom model creation not yet implemented")

    def copy_model(self, source: str, destination: str) -> None:
        """Copy a model"""
        self.model_manager.copy_model(source, destination)

    def running_models(self) -> List[Dict[str, Any]]:
        """List currently running models"""
        return self.inference_engine.get_running_models()

    def ps(self) -> List[Dict[str, Any]]:
        """Alias for running_models"""
        return self.running_models()
