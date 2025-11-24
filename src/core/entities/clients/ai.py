from dataclasses import dataclass

from .abstract_client import AbstractClient


@dataclass
class AI(AbstractClient):
    """AI bot client."""
    is_ai: bool = True  # Override for AI
    
    # Future: can add AI-specific fields like strategy, difficulty, etc.
    # strategy: AIStrategy = AIStrategy.AGGRESSIVE

