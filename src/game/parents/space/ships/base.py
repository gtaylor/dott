from src.game.parents.base_objects.thing import ThingObject
from src.game.parents.space.solar_system import InSpaceObject


class BaseSpaceShipObject(InSpaceObject):
    """
    A generic spaceship. Has attributes like armor/shield and etc. The players
    don't physically sit in this object. This is their ship's "avatar" in
    hangars and space. It holds things like hull/shield condition and
    module loadouts.

    The innards of a ship are objects in the inventory of these
    BaseSpaceShipObject things. Ships are controlled from a
    :py:class:`SpaceShipBridgeObject`.
    """
    pass