from src.game.parents.space.ships.ship_classes.base import BaseSpaceShipObject
from src.game.parents.space.ships.ship_classes.defines import SHIP_CLASS_CODE_SHUTTLE, SHIP_CLASS_SHUTTLE


class BaseShuttleSpaceShipObject(BaseSpaceShipObject):
    """
    Some basic stuff for the Shuttle ship class.
    """

    ship_class = SHIP_CLASS_SHUTTLE
    ship_class_code = SHIP_CLASS_CODE_SHUTTLE