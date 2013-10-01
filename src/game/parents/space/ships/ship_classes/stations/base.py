from src.game.parents.space.ships.ship_classes.base import BaseSpaceShipObject
from src.game.parents.space.ships.ship_classes.defines import SHIP_CLASS_STATION, SHIP_CLASS_CODE_STATION


class BaseSpaceStationObject(BaseSpaceShipObject):
    """
    A basic space station.
    """

    ship_class = SHIP_CLASS_STATION
    ship_class_code = SHIP_CLASS_CODE_STATION