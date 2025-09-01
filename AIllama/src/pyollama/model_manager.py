import os
import json
import shutil
from pathlib import Path
from typing import List, Dict, Optional, Any
import logging
from datetime import datetime

from huggingface_hub import HfApi, snapshot_download, hf_hub_download
from tqdm import tqdm

from .config import Config
from .core import ModelInfo

logger = logging.getLogger(__name__)


class ModelManager:
    """Manages model downloading, storage, and metadata"""

    def __init__(self, config: Config):
        self.config = config
        self.hf_api = HfApi()
        self.config.ensure_directories()

        # Model registry mapping common names to Hugging Face repos
        self.model_registry = {
            # Llama models
            "llama2:7b": "meta-llama/Llama-2-7b-chat-hf",
            "llama2:13b": "meta-llama/Llama-2-13b-chat-hf",
            "llama2:70b": "meta-llama/Llama-2-70b-chat-hf",
            "llama3:8b": "meta-llama/Meta-Llama-3-8B-Instruct",
            "llama3:70b": "meta-llama/Meta-Llama-3-70B-Instruct",

            # Mistral models
            "mistral:7b": "mistralai/Mistral-7B-Instruct-v0.1",
            "mistral:7b-v0.2": "mistralai/Mistral-7B-Instruct-v0.2",
            "mixtral:8x7b": "mistralai/Mixtral-8x7B-Instruct-v0.1",

            # Other popular models
            "phi:2": "microsoft/phi-2",
            "phi:1.5": "microsoft/phi-1_5",
            "gemma:2b": "google/gemma-2b",
            "gemma:7b": "google/gemma-7b",
            "qwen:7b": "Qwen/Qwen1.5-7B-Chat",
            "qwen:14b": "Qwen/Qwen1.5-14B-Chat",
            "qwen2:7b": "Qwen/Qwen2-7B-Instruct",
            "codellama:7b": "codellama/CodeLlama-7b-hf",
            "codellama:13b": "codellama/CodeLlama-13b-hf",
            "codellama:34b": "codellama/CodeLlama-34b-hf",

            # Smaller models for testing
            "tinyllama": "TinyLlama/TinyLlama-1.1B-Chat-v1.0",
            "phi:0.5b": "susnato/phi-1_5-dev",
        }

    def list_models(self) -> List[ModelInfo]:
        """List all available local models"""
        models = []

        # Check for GGUF files
        for gguf_file in self.config.model_dir.glob("**/*.gguf"):
            if gguf_file.is_file():
                model_name = gguf_file.stem
                size = gguf_file.stat().st_size
                modified_time = datetime.fromtimestamp(gguf_file.stat().st_mtime)
                models.append(ModelInfo(
                    name=model_name,
                    size=size,
                    path=str(gguf_file),
                    modified_at=modified_time.isoformat(),
                    format="gguf"
                ))

        # Check for Hugging Face model directories
        for model_dir in self.config.model_dir.iterdir():
            if model_dir.is_dir() and not model_dir.name.startswith('.'):
                # Look for model files in the directory
                model_files = list(model_dir.glob("*.bin")) + list(model_dir.glob("*.safetensors"))
                if model_files:
                    total_size = sum(f.stat().st_size for f in model_files)
                    modified_time = max(f.stat().st_mtime for f in model_files)
                    modified_time = datetime.fromtimestamp(modified_time)
                    models.append(ModelInfo(
                        name=model_dir.name,
                        size=total_size,
                        path=str(model_dir),
                        modified_at=modified_time.isoformat(),
                        format="hf"
                    ))

        return models

    def pull_model(self, model_name: str, force: bool = False) -> None:
        """Download a model from Hugging Face"""
        logger.info(f"Pulling model: {model_name}")

        # Check if model already exists
        if not force and self._model_exists(model_name):
            logger.info(f"Model {model_name} already exists. Use force=True to re-download.")
            return

        # Get the Hugging Face repository
        hf_repo = self.model_registry.get(model_name, model_name)

        try:
            # Try to download as GGUF first (if available)
            gguf_files = self._find_gguf_files(hf_repo)
            if gguf_files:
                self._download_gguf_model(hf_repo, model_name, gguf_files[0])
            else:
                # Download full model
                self._download_hf_model(hf_repo, model_name)

            logger.info(f"Successfully downloaded model: {model_name}")

        except Exception as e:
            logger.error(f"Failed to download model {model_name}: {e}")
            raise

    def _model_exists(self, model_name: str) -> bool:
        """Check if a model already exists locally"""
        # Check for GGUF file
        gguf_path = self.config.model_dir / f"{model_name}.gguf"
        if gguf_path.exists():
            return True

        # Check for model directory
        model_dir = self.config.model_dir / model_name
        if model_dir.exists() and model_dir.is_dir():
            return True

        return False

    def _find_gguf_files(self, hf_repo: str) -> List[str]:
        """Find GGUF files in a Hugging Face repository"""
        try:
            files = self.hf_api.list_repo_files(hf_repo)
            gguf_files = [f for f in files if f.endswith('.gguf')]
            return gguf_files
        except Exception:
            return []

    def _download_gguf_model(self, hf_repo: str, model_name: str, gguf_file: str):
        """Download a GGUF model file"""
        logger.info(f"Downloading GGUF model: {gguf_file}")

        local_path = self.config.model_dir / f"{model_name}.gguf"
        hf_hub_download(
            repo_id=hf_repo,
            filename=gguf_file,
            local_dir=self.config.model_dir,
            local_dir_use_symlinks=False,
        )

        # Rename if necessary
        downloaded_file = self.config.model_dir / gguf_file
        if downloaded_file != local_path:
            downloaded_file.rename(local_path)

    def _download_hf_model(self, hf_repo: str, model_name: str):
        """Download a full Hugging Face model"""
        logger.info(f"Downloading Hugging Face model: {hf_repo}")

        model_dir = self.config.model_dir / model_name
        snapshot_download(
            repo_id=hf_repo,
            local_dir=model_dir,
            local_dir_use_symlinks=False,
        )

    def delete_model(self, model_name: str) -> None:
        """Delete a model"""
        logger.info(f"Deleting model: {model_name}")

        # Check for GGUF file
        gguf_path = self.config.model_dir / f"{model_name}.gguf"
        if gguf_path.exists():
            gguf_path.unlink()
            logger.info(f"Deleted GGUF model: {gguf_path}")
            return

        # Check for model directory
        model_dir = self.config.model_dir / model_name
        if model_dir.exists() and model_dir.is_dir():
            shutil.rmtree(model_dir)
            logger.info(f"Deleted model directory: {model_dir}")
            return

        raise FileNotFoundError(f"Model {model_name} not found")

    def get_model_info(self, model_name: str) -> ModelInfo:
        """Get detailed information about a model"""
        models = self.list_models()
        for model in models:
            if model.name == model_name:
                return model

        raise FileNotFoundError(f"Model {model_name} not found")

    def copy_model(self, source: str, destination: str) -> None:
        """Copy a model to a new name"""
        logger.info(f"Copying model {source} to {destination}")

        # Get source model info
        source_info = self.get_model_info(source)

        if source_info.format == "gguf":
            # Copy GGUF file
            source_path = Path(source_info.path)
            dest_path = self.config.model_dir / f"{destination}.gguf"
            shutil.copy2(source_path, dest_path)
        else:
            # Copy model directory
            source_path = Path(source_info.path)
            dest_path = self.config.model_dir / destination
            if dest_path.exists():
                shutil.rmtree(dest_path)
            shutil.copytree(source_path, dest_path)

        logger.info(f"Successfully copied model {source} to {destination}")

    def get_model_path(self, model_name: str) -> Path:
        """Get the path to a model"""
        # Check for GGUF file
        gguf_path = self.config.model_dir / f"{model_name}.gguf"
        if gguf_path.exists():
            return gguf_path

        # Check for model directory
        model_dir = self.config.model_dir / model_name
        if model_dir.exists() and model_dir.is_dir():
            return model_dir

        raise FileNotFoundError(f"Model {model_name} not found")
