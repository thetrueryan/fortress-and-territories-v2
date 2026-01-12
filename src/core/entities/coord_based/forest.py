from dataclasses import dataclass

from .abstract_cord_entity import AbstractCoordEntity


@dataclass
class Forest(AbstractCoordEntity):
    icon = "^"
    cost = 2