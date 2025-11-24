from dataclasses import dataclass


@dataclass
class GameplayState:
    fog_radius: int = 5
    tower_vision_radius: int = 15
    fortress_capture_cost: int = 3
    bridge_build_cost: int = 5
    bridge_capture_cost: int = 1
    actions_per_turn: int = 6
