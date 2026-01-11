import curses

from src.controllers.camera_controller import CameraController
from src.core.configs.display import DisplayConfig
from src.core.entities.world import World
from src.core.types.coord import Coord
from src.core.types.player_action import PlayerAction
from src.core.types.enums.action_type import PlayerActionType


class InputHandler:
    """Translates raw curses input into high-level player actions."""

    _LMB_FLAGS = (
        "BUTTON1_PRESSED",
        "BUTTON1_CLICKED",
        "BUTTON1_DOUBLE_CLICKED",
        "BUTTON1_RELEASED",
    )
    _RMB_FLAGS = (
        "BUTTON3_PRESSED",
        "BUTTON3_CLICKED",
        "BUTTON3_DOUBLE_CLICKED",
        "BUTTON3_RELEASED",
        "BUTTON2_PRESSED",
        "BUTTON2_CLICKED",
        "BUTTON2_DOUBLE_CLICKED",
        "BUTTON2_RELEASED",
    )

    def __init__(self, display: DisplayConfig, camera: CameraController) -> None:
        self.display = display
        self.camera = camera

    def interpret(self, key: int, world: World | None) -> None | PlayerAction:
        """Convert key code into a player action if applicable."""
        if key != curses.KEY_MOUSE or world is None:
            return None

        try:
            _, mx, my, _, bstate = curses.getmouse()
        except curses.error:
            return None

        if self._pressed(bstate, self._RMB_FLAGS):
            return PlayerAction(kind=PlayerActionType.SKIP)

        if not self._pressed(bstate, self._LMB_FLAGS):
            return None

        game_x = mx - self.display.offset_x + self.camera.camera_x
        game_y = my - self.display.offset_y + self.camera.camera_y

        if not (0 <= game_x < world.width and 0 <= game_y < world.height):
            return None

        return PlayerAction(kind=PlayerActionType.BUILD, coord=Coord(game_x, game_y))

    def _pressed(self, bstate: int, flag_names: tuple[str, ...]) -> bool:
        for name in flag_names:
            flag = getattr(curses, name, None)
            if flag and (bstate & flag):
                return True
        return False

