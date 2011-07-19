from src.game.parents.base_objects.base import BaseObject

class ThingObject(BaseObject):
    """
    'Thing' is somewhat of a generic term, but I'm a loss for what else to
    call it. A thing is anything that can be physically touched, picked up,
    or interacted with. These can be stuff like an ExitObject
    (sub-classes ThingObject), or a weapon, a vehicle, or even a
    PlayerObject (sub-classes ThingObject).

    It is perfectly acceptable to use this class directly if your Thing has no
    special behaviors.

    Unlike a RoomObject, ThingObject has a location, and may be picked up.
    However, a ThingObject can carry other ThingObjects, like a RoomObject.
    """
    def execute_command(self, command_string):
        # This is the 'normal' case in that we just hand the input
        # off to the command handler.
        if not self._command_handler.handle_input(command_string):
            print "NO MATCH"