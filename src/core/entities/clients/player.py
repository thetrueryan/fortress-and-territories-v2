from dataclasses import dataclass

from .abstract_client import AbstractClient


@dataclass
class Player(AbstractClient):
    """Human player client."""
    is_ai: bool = False  # Override for Player

