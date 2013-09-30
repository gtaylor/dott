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

    @property
    def base_type(self):
        """
        Returns this object's type lineage.

        :rtype: str
        :returns: ``'thing'``
        """

        return 'thing'