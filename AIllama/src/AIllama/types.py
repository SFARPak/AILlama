from dataclasses import dataclass
from typing import List, Dict, Optional, Any


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
