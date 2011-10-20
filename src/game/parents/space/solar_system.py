from src.game.parents.base_objects.room import RoomObject
from src.game.parents.base_objects.thing import ThingObject

class SolarSystemObject(RoomObject):
    """
    Represents a solar system that may contain InSpaceObjects.
    """
    pass

class SolarSystemPlaceObject(ThingObject):
    """
    An object in space that may be warped to. These are more or less 'rooms'
    within the solar system.
    """
    pass

class PlanetObject(SolarSystemPlaceObject):
    """
    Planets are stationary objects in space that may be landed on.
    """
    pass

class InSpaceObject(ThingObject):
    """
    All free-floating objects in a solar system. These differ from a Place
    in that they may be fired upon, scanned, and interacted with.
    """
    pass