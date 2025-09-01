import os
from pathlib import Path
from typing import Optional
from dataclasses import dataclass


@dataclass
class Config:
    """Configuration class for AIllama"""

    model_dir: Path = Path.home() / ".AIllama" / "models"
    host: str = "localhost"
    port: int = 11434
    gpu_layers: int = 0
    context_length: int = 2048
    temperature: float = 0.8
    max_tokens: int = 128
    threads: int = 4

    def __post_init__(self):
        """Initialize configuration with environment variables"""
        # Create model directory if it doesn't exist
        self.model_dir.mkdir(parents=True, exist_ok=True)

        # Override with environment variables if set
        if env_model_dir := os.getenv("AIllama_MODEL_DIR"):
            self.model_dir = Path(env_model_dir)
            self.model_dir.mkdir(parents=True, exist_ok=True)

        if env_host := os.getenv("AIllama_HOST"):
            self.host = env_host

        if env_port := os.getenv("AIllama_PORT"):
            self.port = int(env_port)

        if env_gpu_layers := os.getenv("AIllama_GPU_LAYERS"):
            self.gpu_layers = int(env_gpu_layers)

        if env_context_length := os.getenv("AIllama_CONTEXT_LENGTH"):
            self.context_length = int(env_context_length)

        if env_temperature := os.getenv("AIllama_TEMPERATURE"):
            self.temperature = float(env_temperature)

        if env_max_tokens := os.getenv("AIllama_MAX_TOKENS"):
            self.max_tokens = int(env_max_tokens)

        if env_threads := os.getenv("AIllama_THREADS"):
            self.threads = int(env_threads)

    def to_dict(self) -> dict:
        """Convert config to dictionary"""
        return {
            "model_dir": str(self.model_dir),
            "host": self.host,
            "port": self.port,
            "gpu_layers": self.gpu_layers,
            "context_length": self.context_length,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            "threads": self.threads,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Config":
        """Create config from dictionary"""
        config = cls()
        for key, value in data.items():
            if hasattr(config, key):
                if key == "model_dir":
                    value = Path(value)
                setattr(config, key, value)
        return config
