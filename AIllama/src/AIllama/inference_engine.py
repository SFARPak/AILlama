import os
import json
from pathlib import Path
from typing import List, Dict, Optional, Any, Union
import logging

from .config import Config
from .types import GenerateResponse, ChatResponse, ChatMessage

logger = logging.getLogger(__name__)


class InferenceEngine:
    """Handles model inference and text generation"""

    def __init__(self, config: Config):
        self.config = config
        self.loaded_models = {}  # Track loaded models

    def generate(self, model_name: str, prompt: str, **kwargs) -> GenerateResponse:
        """Generate text from a model"""
        # For now, return a mock response since we don't have llama.cpp integration yet
        # This is a placeholder that will be replaced with actual model inference

        logger.info(f"Generating text with model {model_name}")

        # Mock response - in a real implementation, this would load the model and generate text
        mock_response = f"This is a mock response from {model_name}. Prompt: {prompt[:50]}..."

        return GenerateResponse(
            response=mock_response,
            done=True,
            context=[1, 2, 3, 4, 5],  # Mock context tokens
            total_duration=1000000000,  # 1 second in nanoseconds
            load_duration=500000000,   # 0.5 seconds
            prompt_eval_count=len(prompt.split()),
            eval_count=len(mock_response.split()),
            eval_duration=500000000    # 0.5 seconds
        )

    def chat(self, model_name: str, messages: List[Dict[str, str]], **kwargs) -> ChatResponse:
        """Chat with a model"""
        logger.info(f"Chatting with model {model_name}")

        # Extract the last user message for context
        user_messages = [msg for msg in messages if msg.get("role") == "user"]
        last_user_message = user_messages[-1]["content"] if user_messages else "Hello"

        # Mock response
        mock_response = f"Hello! This is a mock response from {model_name}. You said: {last_user_message[:50]}..."

        return ChatResponse(
            message=ChatMessage(role="assistant", content=mock_response),
            done=True,
            total_duration=1000000000,
            load_duration=500000000,
            prompt_eval_count=sum(len(msg["content"].split()) for msg in messages),
            eval_count=len(mock_response.split()),
            eval_duration=500000000
        )

    def embed(self, model_name: str, input_text: Union[str, List[str]]) -> List[float]:
        """Generate embeddings for text"""
        logger.info(f"Generating embeddings with model {model_name}")

        # Mock embeddings - in a real implementation, this would generate actual embeddings
        if isinstance(input_text, str):
            # Simple mock embedding based on text length and content
            import hashlib
            text_hash = hashlib.md5(input_text.encode()).hexdigest()
            embedding = [float(int(text_hash[i:i+2], 16)) / 255.0 for i in range(0, 32, 2)]
            return embedding
        else:
            # For list of texts, return embeddings for each
            embeddings = []
            for text in input_text:
                text_hash = hashlib.md5(text.encode()).hexdigest()
                embedding = [float(int(text_hash[i:i+2], 16)) / 255.0 for i in range(0, 32, 2)]
                embeddings.append(embedding)
            return embeddings[0] if len(embeddings) == 1 else embeddings

    def get_running_models(self) -> List[Dict[str, Any]]:
        """Get list of currently running models"""
        running = []
        for model_name, model_info in self.loaded_models.items():
            running.append({
                "name": model_name,
                "size": model_info.get("size", 0),
                "size_vram": model_info.get("size_vram", 0),
                "digest": model_info.get("digest", ""),
                "details": {
                    "format": "gguf",
                    "family": model_info.get("family", "unknown"),
                    "families": model_info.get("families", ["unknown"]),
                    "parameter_size": model_info.get("parameter_size", "unknown"),
                    "quantization_level": model_info.get("quantization_level", "unknown")
                },
                "expires_at": model_info.get("expires_at", "")
            })
        return running

    def load_model(self, model_name: str) -> None:
        """Load a model into memory"""
        if model_name in self.loaded_models:
            logger.info(f"Model {model_name} already loaded")
            return

        logger.info(f"Loading model {model_name}")

        # Mock model loading - in a real implementation, this would load the actual model
        self.loaded_models[model_name] = {
            "size": 4000000000,  # 4GB mock size
            "size_vram": 4000000000,
            "digest": f"mock_digest_{model_name}",
            "family": "llama",
            "families": ["llama"],
            "parameter_size": "7B",
            "quantization_level": "Q4_K_M",
            "expires_at": ""
        }

    def unload_model(self, model_name: str) -> None:
        """Unload a model from memory"""
        if model_name in self.loaded_models:
            logger.info(f"Unloading model {model_name}")
            del self.loaded_models[model_name]

    def is_model_loaded(self, model_name: str) -> bool:
        """Check if a model is currently loaded"""
        return model_name in self.loaded_models
