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

    def at_session_connect_event(self):
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

    def at_session_disconnect_event(self):
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