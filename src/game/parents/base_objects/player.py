from src.game.parents.base_objects.thing import ThingObject

class PlayerObject(ThingObject):
    """
    All players inherit this parent class. It further extends ThingObject with
    player-specific behavior.
    """

    #
    ## Begin events
    #

    def at_player_connect_event(self):
        """
        This is called when a PlayerAccount logs in. Whatever object it is
        controlling has this method called on it.
        """
        neighbors = self.location.get_contents()

        for neighbor in neighbors:
            if neighbor is not self:
                neighbor.emit_to("%s has connected." % self.name)

    def at_player_disconnect_event(self):
        """
        This is called when a PlayerAccount disconnects. Whatever object it is
        controlling has this method called on it.
        """
        neighbors = self.location.get_contents()

        for neighbor in neighbors:
            if neighbor is not self:
                neighbor.emit_to("%s has disconnected." % self.name)