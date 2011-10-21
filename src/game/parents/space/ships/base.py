from src.game.parents.space.hangar import HangarMixin
from src.game.parents.space.ships import defines as ship_defines
from src.game.parents.space.ships.interior.bridge import SpaceShipBridgeObject
from src.game.parents.space.solar_system import InSpaceObject

class ShipError(BaseException):
    """
    Raise this when something unexpected ship-related happens.
    """
    pass

class BaseSpaceShipObject(InSpaceObject):
    """
    A generic spaceship. Has attributes like armor/shield and etc. The players
    don't physically sit in this object. This is their ship's "avatar" in
    hangars and space. It holds things like hull/shield condition and
    module loadouts.

    The innards of a ship are objects in the inventory of these
    BaseSpaceShipObject things. Ships are controlled from a
    :py:class:`SpaceShipBridgeObject`.
    """
    # This is the ship type that is displayed in contacts and messages.
    ship_type_name = 'Unknown'
    # Ship size class. IE: Shuttle, frigate, cruiser, etc.
    ship_class = ship_defines.SHIP_CLASS_SHUTTLE

    # These parents are used to construct various interior objects in the ship.
    # Any None values here means said interior object does not exist
    # in this ship.
    bridge_parent = 'src.game.parents.space.ships.interior.bridge.SpaceShipBridgeObject'

    def is_ship_landed(self):
        """
        Returns True if this ship is landed/docked, False if not.

        :rtype: bool
        :returns: True if the ship is landed, False if not.
        """
        # If the ship is in a hangar, it's landed/docked.
        return isinstance(self.location, HangarMixin)

    def get_bridge_obj(self):
        """
        Finds the SpaceShipBridgeObject that controls the ship.

        :rtype: SpaceShipBridgeObject
        :returns: The bridge that controls the ship.
        :raises: ShipError if no bridge was found.
        """
        contents = self.get_contents()
        for obj in contents:
            if isinstance(obj, SpaceShipBridgeObject):
                return obj

        raise ShipError("No bridge found for ship #s." % self.id)

    def emit_to_interior(self, message):
        """
        Emits a message to the entire interior of the ship. The entire
        crew should hear this.

        :param str message: The message to emit to the interior of the ship.
        """
        contents = self.get_contents()
        for obj in contents:
            obj.emit_to_contents(message)

    def start_launch_sequence(self):
        """
        Starts the launching sequence from within a hangar.
        """
        bridge = self.get_bridge_obj()
        hangar = self.location

        self.emit_to_interior("The ship lurches as enters space.")
        launch_to = hangar.get_launchto_location()
        self.move_to(launch_to)
        bridge.emit_to_contents("Your ship is now by %s in %s" % (
            # Name of the SolarSystemPlaceObject the ship is floating near.
            launch_to.name,
            # Solar system name
            launch_to.location.name,
        ))
