"""
Contains exit-related stuff.
"""

from src.game.parents.base_objects.base import BaseObject


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
        :raises: NoSuchObject if the ID can't be found in the DB.
        """

        return self._object_store.get_object(self.destination_id)

    def set_destination(self, obj_or_id):
        """
        Sets the object's destination.

        :type obj_or_id: int or BaseObject
        :param obj_or_id: The new destination for the object in ID or
            BaseObject instance form.
        """

        self._generic_baseobject_to_id_property_setter('destination_id', obj_or_id)

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
