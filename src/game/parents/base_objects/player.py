from src.game.parents.base_objects.thing import ThingObject

class PlayerObject(ThingObject):
    """
    All players inherit this parent class. It further extends ThingObject with
    player-specific behavior.
    """

    @property
    def base_type(self):
        """
        Return's this object's type lineage.

        :rtype: str
        :returns: ``'player'``
        """
        return 'player'

    #
    ## Begin events
    #

    def after_session_connect_event(self):
        """
        This is called when the proxy authenticates and logs in a Session that
        controls this object. This event is only triggered when the first
        Session controlling this object is logged in. For example, logging in
        a second time with another client would not trigger this again.
        """
        neighbors = self.location.get_contents()

        for neighbor in neighbors:
            if neighbor is not self:
                neighbor.emit_to("%s has connected." % self.name)

    def after_session_disconnect_event(self):
        """
        This is called when the last Sesssion that controls this object is
        disconnected. If you have two clients open that are authenticated and
        controlling the same object, this will not trigger until the last
        Session is closed.
        """
        neighbors = self.location.get_contents()

        for neighbor in neighbors:
            if neighbor is not self:
                neighbor.emit_to("%s has disconnected." % self.name)


class AdminPlayerObject(PlayerObject):
    """
    Parent for admin players. Changes or overrides some behaviors.
    """

    def is_admin(self):
        """
        This always returns ``True``, since this is a AdminPlayerObject.

        :rtype: bool
        :returns: ``True``
        """
        return True