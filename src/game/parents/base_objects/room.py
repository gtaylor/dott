from src.game.parents.base_objects.base import BaseObject

class RoomObject(BaseObject):
    """
    All rooms inherit this parent class. It further extends BaseObject with
    room-specific behavior.
    """
    @property
    def location(self):
        """
        Rooms never have a location.
        """
        return None