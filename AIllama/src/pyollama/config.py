import os
from pathlib import Path
from typing import Optional
import json


class Config:
    """Configuration class for PyOllama"""

    def __init__(self):
        # Model directory
        self.model_dir = Path.home() / ".pyollama" / "models"

        # Server configuration
        self.host = "localhost"
        self.port = 11434

        # GPU configuration
        self.gpu_layers = -1  # -1 = auto, 0 = CPU only
        self.main_gpu = 0
        self.tensor_split = None

        # Model loading configuration
        self.context_length = 2048
        self.threads = None  # Auto-detect
        self.batch_size = 512

        # Generation parameters
        self.temperature = 0.8
        self.top_p = 0.9
        self.top_k = 40
        self.repeat_penalty = 1.1
        self.repeat_last_n = 64

        # Cache configuration
        self.cache_dir = Path.home() / ".pyollama" / "cache"

        # Logging
        self.log_level = "INFO"
        self.log_file = None

        # Load from environment variables and config file
        self._load_from_env()
        self._load_from_file()

    def _load_from_env(self):
        """Load configuration from environment variables"""
        env_mappings = {
            'PYOLLAMA_MODEL_DIR': 'model_dir',
            'PYOLLAMA_HOST': 'host',
            'PYOLLAMA_PORT': 'port',
            'PYOLLAMA_GPU_LAYERS': 'gpu_layers',
            'PYOLLAMA_MAIN_GPU': 'main_gpu',
            'PYOLLAMA_CONTEXT_LENGTH': 'context_length',
            'PYOLLAMA_THREADS': 'threads',
            'PYOLLAMA_BATCH_SIZE': 'batch_size',
            'PYOLLAMA_TEMPERATURE': 'temperature',
            'PYOLLAMA_TOP_P': 'top_p',
            'PYOLLAMA_TOP_K': 'top_k',
            'PYOLLAMA_REPEAT_PENALTY': 'repeat_penalty',
            'PYOLLAMA_REPEAT_LAST_N': 'repeat_last_n',
            'PYOLLAMA_CACHE_DIR': 'cache_dir',
            'PYOLLAMA_LOG_LEVEL': 'log_level',
            'PYOLLAMA_LOG_FILE': 'log_file',
        }

        for env_var, attr in env_mappings.items():
            value = os.getenv(env_var)
            if value is not None:
                if attr in ['model_dir', 'cache_dir']:
                    setattr(self, attr, Path(value))
                elif attr in ['port', 'gpu_layers', 'main_gpu', 'context_length', 'threads', 'batch_size', 'top_k', 'repeat_last_n']:
                    setattr(self, attr, int(value))
                elif attr in ['temperature', 'top_p', 'repeat_penalty']:
                    setattr(self, attr, float(value))
                else:
                    setattr(self, attr, value)

    def _load_from_file(self):
        """Load configuration from config file"""
        config_file = Path.home() / ".pyollama" / "config.json"
        if config_file.exists():
            try:
                with open(config_file, 'r') as f:
                    config_data = json.load(f)

                for key, value in config_data.items():
                    if hasattr(self, key):
                        if key in ['model_dir', 'cache_dir']:
                            setattr(self, key, Path(value))
                        else:
                            setattr(self, key, value)
            except (json.JSONDecodeError, IOError) as e:
                print(f"Warning: Could not load config file {config_file}: {e}")

    def save_to_file(self):
        """Save current configuration to file"""
        config_file = Path.home() / ".pyollama" / "config.json"
        config_file.parent.mkdir(parents=True, exist_ok=True)

        config_data = {}
        for attr in dir(self):
            if not attr.startswith('_') and not callable(getattr(self, attr)):
                value = getattr(self, attr)
                if isinstance(value, Path):
                    config_data[attr] = str(value)
                else:
                    config_data[attr] = value

        with open(config_file, 'w') as f:
            json.dump(config_data, f, indent=2)

    def ensure_directories(self):
        """Ensure all necessary directories exist"""
        self.model_dir.mkdir(parents=True, exist_ok=True)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
