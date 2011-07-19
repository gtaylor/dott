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

    def execute_command(self, command_string):
        """
        Rooms can not execute commands, since they can't be controlled.
        """
        pass

    def emit_to(self, message):
        """
        Rooms can not receive emits, since they can't be controlled.
        """
        pass