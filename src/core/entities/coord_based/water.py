from dataclasses import dataclass

from .abstract_cord_entity import AbstractCoordEntity


@dataclass
class Water(AbstractCoordEntity):
    icon = "~"
    cost = 5