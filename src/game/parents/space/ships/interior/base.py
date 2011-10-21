from src.game.parents.base_objects.thing import ThingObject

class SpaceShipInteriorObject(ThingObject):
    """
    These objects represent locations within the interior of a ship. They
    can be non-functional stuff like crew quarters, or important things like
    the bridge. To the player, these look and feel like rooms, but they're
    really objects sitting inside the BaseSpaceShipObject's inventory.
    """
    def get_ship_obj(self):
        """
        Returns the ship object which this interior object belongs to.

        :rtype: BaseSpaceShipObject
        :returns: The ship this interior object is a part of. Will be in
            the form of a BaseSpaceShipObject sub-classed instance.
        """
        return self.location