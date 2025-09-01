import os
import time
import threading
from pathlib import Path
from typing import List, Dict, Optional, Any, Union
import logging

import llama_cpp
import numpy as np
from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline

from .config import Config
from .core import GenerateResponse, ChatResponse, ChatMessage

logger = logging.getLogger(__name__)


class InferenceEngine:
    """Handles model loading and inference operations"""

    def __init__(self, config: Config):
        self.config = config
        self.loaded_models = {}  # Cache for loaded models
        self.model_locks = {}  # Thread locks for each model
        self.running_models = {}  # Track running models

    def generate(self, model_name: str, prompt: str, **kwargs) -> GenerateResponse:
        """Generate text from a model"""
        start_time = time.time()

        # Get or load the model
        model = self._get_model(model_name)

        # Merge generation parameters
        gen_kwargs = self._get_generation_kwargs(kwargs)

        try:
            # Generate text
            if isinstance(model, llama_cpp.Llama):
                # GGUF model
                output = model(prompt, **gen_kwargs)
                response_text = output['choices'][0]['text']
                context = output.get('usage', {}).get('prompt_eval_count', 0)
                eval_count = output.get('usage', {}).get('completion_tokens', 0)
            else:
                # Hugging Face model
                inputs = model.tokenizer(prompt, return_tensors="pt")
                if hasattr(model.model, 'device'):
                    inputs = {k: v.to(model.model.device) for k, v in inputs.items()}

                with torch.no_grad():
                    outputs = model.model.generate(
                        **inputs,
                        max_new_tokens=gen_kwargs.get('max_tokens', 128),
                        temperature=gen_kwargs.get('temperature', self.config.temperature),
                        top_p=gen_kwargs.get('top_p', self.config.top_p),
                        top_k=gen_kwargs.get('top_k', self.config.top_k),
                        do_sample=True,
                        pad_token_id=model.tokenizer.eos_token_id
                    )

                response_text = model.tokenizer.decode(outputs[0][inputs['input_ids'].shape[1]:], skip_special_tokens=True)
                context = inputs['input_ids'].shape[1]
                eval_count = outputs.shape[1] - inputs['input_ids'].shape[1]

            total_duration = int((time.time() - start_time) * 1e9)  # nanoseconds

            return GenerateResponse(
                response=response_text,
                done=True,
                context=[0] * context if context else None,  # Simplified context
                total_duration=total_duration,
                prompt_eval_count=context,
                eval_count=eval_count
            )

        except Exception as e:
            logger.error(f"Error generating text: {e}")
            raise

    def chat(self, model_name: str, messages: List[Dict[str, str]], **kwargs) -> ChatResponse:
        """Chat with a model"""
        start_time = time.time()

        # Get or load the model
        model = self._get_model(model_name)

        # Format messages for the model
        formatted_prompt = self._format_chat_messages(messages)

        # Generate response
        gen_response = self.generate(model_name, formatted_prompt, **kwargs)

        # Extract the assistant's response
        response_text = gen_response.response

        # Create chat message
        chat_message = ChatMessage(role="assistant", content=response_text)

        total_duration = int((time.time() - start_time) * 1e9)

        return ChatResponse(
            message=chat_message,
            done=True,
            total_duration=total_duration,
            prompt_eval_count=gen_response.prompt_eval_count,
            eval_count=gen_response.eval_count
        )

    def embed(self, model_name: str, input_text: Union[str, List[str]]) -> List[float]:
        """Generate embeddings for text"""
        # Get or load the model
        model = self._get_model(model_name)

        if isinstance(model, llama_cpp.Llama):
            # For GGUF models, we can use the built-in embedding functionality
            if isinstance(input_text, str):
                embedding = model.embed(input_text)
            else:
                # Average embeddings for multiple texts
                embeddings = [model.embed(text) for text in input_text]
                embedding = np.mean(embeddings, axis=0).tolist()
        else:
            # For Hugging Face models, use a simple approach
            # This is a simplified implementation
            if isinstance(input_text, str):
                # Simple token-based embedding (not very good)
                tokens = model.tokenizer.encode(input_text)
                embedding = [float(token) / model.tokenizer.vocab_size for token in tokens[:512]]
                # Pad or truncate to fixed size
                if len(embedding) < 512:
                    embedding.extend([0.0] * (512 - len(embedding)))
                else:
                    embedding = embedding[:512]
            else:
                embeddings = []
                for text in input_text:
                    tokens = model.tokenizer.encode(text)
                    emb = [float(token) / model.tokenizer.vocab_size for token in tokens[:512]]
                    if len(emb) < 512:
                        emb.extend([0.0] * (512 - len(emb)))
                    else:
                        emb = emb[:512]
                    embeddings.append(emb)
                embedding = np.mean(embeddings, axis=0).tolist()

        return embedding

    def _get_model(self, model_name: str):
        """Get or load a model"""
        if model_name not in self.loaded_models:
            self._load_model(model_name)

        return self.loaded_models[model_name]

    def _load_model(self, model_name: str):
        """Load a model into memory"""
        from .model_manager import ModelManager
        model_manager = ModelManager(self.config)

        try:
            model_path = model_manager.get_model_path(model_name)
            model_info = model_manager.get_model_info(model_name)

            logger.info(f"Loading model: {model_name}")

            if model_info.format == "gguf":
                # Load GGUF model with llama.cpp
                model = llama_cpp.Llama(
                    model_path=str(model_path),
                    n_ctx=self.config.context_length,
                    n_threads=self.config.threads or os.cpu_count(),
                    n_gpu_layers=self.config.gpu_layers,
                    verbose=False
                )
            else:
                # Load Hugging Face model
                import torch
                tokenizer = AutoTokenizer.from_pretrained(str(model_path))
                model = AutoModelForCausalLM.from_pretrained(
                    str(model_path),
                    torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
                    device_map="auto" if torch.cuda.is_available() else None,
                    low_cpu_mem_usage=True
                )

                # Create a simple wrapper
                class HFModelWrapper:
                    def __init__(self, model, tokenizer):
                        self.model = model
                        self.tokenizer = tokenizer

                model = HFModelWrapper(model, tokenizer)

            self.loaded_models[model_name] = model
            self.model_locks[model_name] = threading.Lock()

            # Track as running
            self.running_models[model_name] = {
                "name": model_name,
                "size": model_info.size,
                "path": model_info.path,
                "loaded_at": time.time()
            }

            logger.info(f"Successfully loaded model: {model_name}")

        except Exception as e:
            logger.error(f"Failed to load model {model_name}: {e}")
            raise

    def _get_generation_kwargs(self, kwargs: Dict[str, Any]) -> Dict[str, Any]:
        """Get generation parameters with defaults"""
        defaults = {
            'max_tokens': 128,
            'temperature': self.config.temperature,
            'top_p': self.config.top_p,
            'top_k': self.config.top_k,
            'repeat_penalty': self.config.repeat_penalty,
            'repeat_last_n': self.config.repeat_last_n,
        }

        # Update with provided kwargs
        defaults.update(kwargs)
        return defaults

    def _format_chat_messages(self, messages: List[Dict[str, str]]) -> str:
        """Format chat messages for the model"""
        formatted = []

        for msg in messages:
            role = msg.get('role', '')
            content = msg.get('content', '')

            if role == 'system':
                formatted.append(f"System: {content}")
            elif role == 'user':
                formatted.append(f"User: {content}")
            elif role == 'assistant':
                formatted.append(f"Assistant: {content}")

        return "\n\n".join(formatted) + "\n\nAssistant:"

    def unload_model(self, model_name: str):
        """Unload a model from memory"""
        if model_name in self.loaded_models:
            del self.loaded_models[model_name]
            if model_name in self.running_models:
                del self.running_models[model_name]
            logger.info(f"Unloaded model: {model_name}")

    def get_running_models(self) -> List[Dict[str, Any]]:
        """Get list of currently running models"""
        return list(self.running_models.values())

    def get_model_lock(self, model_name: str) -> threading.Lock:
        """Get the lock for a specific model"""
        if model_name not in self.model_locks:
            self.model_locks[model_name] = threading.Lock()
        return self.model_locks[model_name]
