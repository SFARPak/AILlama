import os
import json
import hashlib
import requests
from pathlib import Path
from typing import List, Dict, Optional, Any
from dataclasses import dataclass
import logging

from .config import Config
from .types import ModelInfo

logger = logging.getLogger(__name__)


class ModelManager:
    """Manages model downloading, storage, and metadata"""

    def __init__(self, config: Config):
        self.config = config
        self.models_dir = config.model_dir
        self.models_dir.mkdir(parents=True, exist_ok=True)

        # Model registry - maps model names to download URLs
        self.model_registry = {
            # Llama models
            "llama2:7b": "https://huggingface.co/TheBloke/Llama-2-7B-GGUF/resolve/main/llama-2-7b.Q4_K_M.gguf",
            "llama2:13b": "https://huggingface.co/TheBloke/Llama-2-13B-GGUF/resolve/main/llama-2-13b.Q4_K_M.gguf",
            "llama3:8b": "https://huggingface.co/TheBloke/Llama-3-8B-Instruct-GGUF/resolve/main/llama-3-8b-instruct.Q4_K_M.gguf",
            "llama3:70b": "https://huggingface.co/TheBloke/Llama-3-70B-Instruct-GGUF/resolve/main/llama-3-70b-instruct.Q4_K_M.gguf",

            # Mistral models
            "mistral:7b": "https://huggingface.co/TheBloke/Mistral-7B-Instruct-v0.1-GGUF/resolve/main/mistral-7b-instruct-v0.1.Q4_K_M.gguf",
            "mixtral:8x7b": "https://huggingface.co/TheBloke/Mixtral-8x7B-Instruct-v0.1-GGUF/resolve/main/mixtral-8x7b-instruct-v0.1.Q4_K_M.gguf",

            # Other models
            "codellama:7b": "https://huggingface.co/TheBloke/CodeLlama-7B-Instruct-GGUF/resolve/main/codellama-7b-instruct.Q4_K_M.gguf",
            "codellama:13b": "https://huggingface.co/TheBloke/CodeLlama-13B-Instruct-GGUF/resolve/main/codellama-13b-instruct.Q4_K_M.gguf",
            "phi:2": "https://huggingface.co/TheBloke/phi-2-GGUF/resolve/main/phi-2.Q4_K_M.gguf",
            "gemma:7b": "https://huggingface.co/google/gemma-7b-it/resolve/main/gemma-7b-it.gguf",

            # Tiny models for testing
            "tinyllama": "https://huggingface.co/TheBloke/TinyLlama-1.1B-Chat-v1.0-GGUF/resolve/main/tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf",
        }

    def list_models(self) -> List[ModelInfo]:
        """List all available models"""
        models = []

        # Check for local model files
        for model_file in self.models_dir.glob("*.gguf"):
            if model_file.is_file():
                model_info = self._get_model_info_from_file(model_file)
                if model_info:
                    models.append(model_info)

        # Also check for model directories
        for model_dir in self.models_dir.iterdir():
            if model_dir.is_dir():
                # Look for any .gguf file in the directory
                for gguf_file in model_dir.glob("*.gguf"):
                    if gguf_file.is_file():
                        model_info = self._get_model_info_from_file(gguf_file)
                        if model_info:
                            models.append(model_info)

        return models

    def _get_model_info_from_file(self, model_file: Path) -> Optional[ModelInfo]:
        """Extract model information from a model file"""
        try:
            stat = model_file.stat()
            model_name = model_file.stem

            # Try to get model name from registry (reverse lookup)
            registry_name = None
            for name, url in self.model_registry.items():
                if model_name in url or name.replace(":", "-") in model_name:
                    registry_name = name
                    break

            if not registry_name:
                registry_name = model_name

            return ModelInfo(
                name=registry_name,
                size=stat.st_size,
                path=str(model_file),
                modified_at=str(stat.st_mtime),
                format="gguf",
                parameters={"file_size": stat.st_size}
            )
        except Exception as e:
            logger.warning(f"Failed to get info for model file {model_file}: {e}")
            return None

    def pull_model(self, model_name: str, force: bool = False) -> None:
        """Download a model from Hugging Face"""
        if model_name not in self.model_registry:
            raise ValueError(f"Model '{model_name}' not found in registry. Available models: {list(self.model_registry.keys())}")

        download_url = self.model_registry[model_name]

        # Create model directory
        model_dir = self.models_dir / model_name.replace(":", "-")
        model_dir.mkdir(parents=True, exist_ok=True)

        # Determine filename from URL
        filename = download_url.split("/")[-1]
        model_path = model_dir / filename

        # Check if model already exists
        if model_path.exists() and not force:
            logger.info(f"Model {model_name} already exists at {model_path}")
            return

        logger.info(f"Downloading model {model_name} from {download_url}")

        try:
            # Download the model
            response = requests.get(download_url, stream=True)
            response.raise_for_status()

            total_size = int(response.headers.get('content-length', 0))

            with open(model_path, 'wb') as f:
                downloaded = 0
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)

                        if total_size > 0:
                            progress = (downloaded / total_size) * 100
                            logger.info(f"Download progress: {progress:.1f}%")

            logger.info(f"Successfully downloaded model {model_name} to {model_path}")

        except Exception as e:
            # Clean up partial download
            if model_path.exists():
                model_path.unlink()
            raise Exception(f"Failed to download model {model_name}: {e}")

    def delete_model(self, model_name: str) -> None:
        """Delete a model"""
        # Find the model file
        model_path = None

        # Check for direct model file
        for model_file in self.models_dir.glob("*.gguf"):
            if model_name in model_file.stem:
                model_path = model_file
                break

        # Check for model directory
        model_dir = self.models_dir / model_name.replace(":", "-")
        if model_dir.exists():
            model_file = model_dir / f"{model_name.replace(':', '-')}.gguf"
            if model_file.exists():
                model_path = model_file

        if not model_path:
            raise ValueError(f"Model '{model_name}' not found")

        # Delete the model
        try:
            model_path.unlink()

            # Remove empty directory if it exists
            model_dir = model_path.parent
            if model_dir != self.models_dir and not list(model_dir.iterdir()):
                model_dir.rmdir()

            logger.info(f"Successfully deleted model {model_name}")

        except Exception as e:
            raise Exception(f"Failed to delete model {model_name}: {e}")

    def get_model_info(self, model_name: str) -> ModelInfo:
        """Get information about a specific model"""
        models = self.list_models()
        for model in models:
            if model.name == model_name:
                return model

        raise ValueError(f"Model '{model_name}' not found")

    def copy_model(self, source: str, destination: str) -> None:
        """Copy a model to a new name"""
        # Find source model
        source_info = self.get_model_info(source)

        # Create destination path
        dest_dir = self.models_dir / destination.replace(":", "-")
        dest_dir.mkdir(parents=True, exist_ok=True)
        dest_path = dest_dir / f"{destination.replace(':', '-')}.gguf"

        try:
            # Copy the model file
            import shutil
            shutil.copy2(source_info.path, dest_path)
            logger.info(f"Successfully copied model from {source} to {destination}")

        except Exception as e:
            # Clean up partial copy
            if dest_path.exists():
                dest_path.unlink()
            raise Exception(f"Failed to copy model from {source} to {destination}: {e}")

    def get_available_models(self) -> List[str]:
        """Get list of available model names in registry"""
        return list(self.model_registry.keys())
