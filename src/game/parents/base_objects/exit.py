from src.game.parents.base_objects.base import BaseObject
from src.daemons.server.objects.exceptions import InvalidObjectId


class ExitObject(BaseObject):
    """
    An 'Exit' is used for moving from one location to another. The command
    handler checks a player's location for an exit's name/alias that matches
    the user's input. If a match is found, the player moves to the exit's
    destination.
    """

    #
    ## Begin properties.
    #

    def get_destination(self):
        """
        Returns the object's destination.

        :rtype: BaseObject or ``None``.
        :returns: A reference to the exit's destination BaseObject. If no
            destination is set, or the destination has been destroyed, this
            returns ``None``.
        """

        try:
            return self._object_store.get_object(self.destination_id)
        except InvalidObjectId:
            return None

    def set_destination(self, obj_or_id):
        """
        Sets the object's destination.

        :type obj_or_id: int or BaseObject
        :param obj_or_id: The new destination for the object in ID or
            BaseObject instance form.
        """

        if not obj_or_id:
            # Clear the destination.
            self.destination_id = None
        elif isinstance(obj_or_id, int):
            # Already an int, assume this is an object ID.
            self.destination_id = obj_or_id
        elif isinstance(obj_or_id, basestring):
            # TODO: This should be removable in the future.
            raise Exception("ExitObject.set_destination() can't accept strings: %s" % obj_or_id)
        else:
            # Looks like a BaseObject sub-class. Grab the object ID.
            self.destination_id = obj_or_id.id
    destination = property(get_destination, set_destination)

    @property
    def base_type(self):
        """
        Returns this object's type lineage.

        :rtype: str
        :returns: ``'exit'``
        """

        return 'exit'

    #
    ## Begin methods
    #

    def pass_object_through(self, obj):
        """
        Attempts to pass an object through this exit. Takes into consideration
        any additional locks/permissions.

        :param BaseObject obj: The object to attempt to pass through this
            exit.
        """

        if not self.destination:
            obj.emit_to('That exit leads to nowhere.')
            return

        # Move the object on through to destination.
        obj.move_to(self.destination)

