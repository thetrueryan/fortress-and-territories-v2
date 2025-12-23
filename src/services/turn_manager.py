"""
Turn manager service.
"""

from src.core.states.gameplay import GameplayState


class TurnManager:
    """
    Manages turn order and action budget.

    Tracks current player index and remaining actions per turn.
    """

    def __init__(self, gameplay_state: GameplayState) -> None:
        """
        Initialize turn manager.

        Args:
            gameplay_state: Gameplay state containing actions_per_turn
        """
        self.gameplay_state = gameplay_state
        self.move_budget = gameplay_state.actions_per_turn
        self.current_index = 0
        self.moves_left = self.move_budget

    def reset(self) -> None:
        """Reset to first player with full action budget."""
        self.current_index = 0
        self.moves_left = self.move_budget

    def set_index(self, idx: int) -> None:
        """
        Set current player index and reset action budget.

        Args:
            idx: Player index to set
        """
        self.current_index = idx
        self.moves_left = self.move_budget

    def consume(self, amount: int) -> None:
        """
        Consume action points.

        Args:
            amount: Number of action points to consume
        """
        self.moves_left -= amount

    def needs_advance(self) -> bool:
        """
        Check if turn should advance to next player.

        Returns:
            True if no actions left
        """
        return self.moves_left <= 0

    def advance(self, total_factions: int) -> None:
        """
        Advance to next player's turn.

        Args:
            total_factions: Total number of factions (for wrapping)
        """
        self.current_index = (self.current_index + 1) % total_factions
        self.moves_left = self.move_budget
