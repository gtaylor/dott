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
        destination_id = self._odata.get('destination_id')
        try:
            return self._object_store.get_object(destination_id)
        except InvalidObjectId:
            return None

    def set_destination(self, destination):
        """
        Sets the object's destination.

        :type destination: str or BaseObject
        :param destination: The new destination for the object, in ID or
            BaseObject instance form.
        """
        if not destination:
            # Clear the destination.
            destination = None
        elif not isinstance(destination, basestring):
            # This is probably a BaseObject sub-class. We need to store the
            # object's ID instead of the object itself.
            destination = destination.id
        self._odata['destination_id'] = destination
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

