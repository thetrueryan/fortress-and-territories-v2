"""
Game mode flags.

Provides a single container for all togglable rules that affect build validation.
"""

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class GameModeFlags:
    """
    Aggregates all gameplay mode toggles that influence build validation logic.

    Attributes:
        classic: Fortress capture is disabled (Classic mode). False means Conquest mode.
        supply:  Requires continuous supply chain from base (Supply experimental mode).
        mountain_efficiency: Converted mountains cost 1 AP instead of base cost.
    """

    classic: bool = False
    supply: bool = False
    mountain_efficiency: bool = False
