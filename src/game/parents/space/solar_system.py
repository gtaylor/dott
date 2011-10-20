from src.game.parents.base_objects.room import RoomObject
from src.game.parents.base_objects.thing import ThingObject

class SolarSystemObject(RoomObject):
    """
    Represents a solar system that may contain InSpaceObjects.
    """
    pass

class InSpaceObject(ThingObject):
    """
    All objects that are physically in space inherit from this class.
    """
    pass

class PlanetObject(InSpaceObject):
    """
    Planets are stationary objects in space that may be landed on.
    """
    pass