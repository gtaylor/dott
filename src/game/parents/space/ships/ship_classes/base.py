from src.game.parents.space.hangar import HangarMixin
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

    # This is the full name of the ship type.
    ship_type_name = 'Unknown'
    # The alphanumerical ship reference code.
    ship_reference = 'UNK-NOWN'
    # Ship size class. IE: Shuttle, frigate, cruiser, etc.
    ship_class = 'Unknown'
    ship_class_code = '?'

    # These parents are used to construct various interior objects in the ship.
    # Any None values here means said interior object does not exist
    # in this ship.
    bridge_parent = 'src.game.parents.space.ships.interior.bridge.SpaceShipBridgeObject'

    @property
    def display_name(self):
        """
        :rtype: basestring
        :returns: The value to show on contacts for this ship.
        """

        return self.ship_type_name

    def can_object_enter(self, obj):
        """
        Determine whether another object can enter this ship.

        :param BaseObject obj: The object to check enter permissions for.
        :rtype: tuple
        :returns: A tuple in the format of ``(can_enter, message)``, where
            ``can_enter`` is a bool, and ``message`` is a string or ``None``,
            used to provide a reason for the object not being able to enter.
        """

        # Everyone can enter everything, for now.
        return True, None

    def determine_enter_destination(self, obj):
        """
        Those entering ships should enter to the bridge, not this ship
        object.

        :param BaseObject obj: The other object that is entering this one.
        :rtype: SpaceShipBridgeObject
        :returns: The ship's bridge.
        """

        return self.get_bridge_obj()

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

        raise ShipError("No bridge found for %s" % self.get_appearance_name(
            None, force_admin_view=True))

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

    def get_solar_system_obj(self):
        """
        Regardless of the location of the ship, return which solar system
        the ship is in.

        :rtype: SolarSystemObject or ``None``
        :returns: The solar system the ship is in, or ``None`` if we can't
            figure it out.
        """

        if self.location and hasattr(self.location, 'get_solar_system_obj'):
            return self.location.get_solar_system_obj()

    def get_visible_contacts(self):
        """
        :rtype: list
        :returns: A list of visible contacts in space (from the perspective
            of the invoking ship).
        """

        assert not self.is_ship_landed(), "Attempting to get contacts while landed."
        return [obj for obj in self.location.get_contents()
                if isinstance(obj, InSpaceObject) and obj.id != self.id]

    def check_ship_standing(self, inquiring_ship):
        """
        Used by other ships to check their standing with this ship.

        :param BaseSpaceShipObject inquiring_ship: The ship that wants to
            know their standing to this one.
        :rtype: float
        :returns: A scale between 0.0 and 1.0, with 0.0 being extremely
            hostile, 0.5 being neutral, and 1.0 being extremely friendly.
        """

        # TODO: Make this work.
        return 0.5

    #
    ## Ship vitals

    def is_ship_destroyed(self):
        """
        :rtype: bool
        :returns: True if this ship is destroyed, False if not.
        """

        # TODO: Make this work.
        return False

    def get_max_shield_hp(self):
        """
        :rtype: int
        :returns: The maximum shield HPs for this ship, as currently configured.
        """

        # TODO: Make this work.
        return 100

    def get_current_shield_hp(self):
        """
        :rtype: int
        :returns: The current shield HPs for this ship.
        """

        # TODO: Make this work.
        return 80

    def get_max_hull_hp(self):
        """
        :rtype: int
        :returns: The maximum hull HPs for this ship, as currently configured.
        """

        # TODO: Make this work.
        return 100

    def get_current_hull_hp(self):
        """
        :rtype: int
        :returns: The current hull HPs for this ship.
        """

        # TODO: Make this work.
        return 50

    def get_max_power_units(self):
        """
        :rtype: int
        :returns: The maximum number of power units the ship is capable of
            producing in its current state.
        """

        # TODO: Make this work.
        return 10

    def get_total_power_unit_usage(self):
        """
        :rtype: int
        :returns: The current power usage in power units.
        """

        return self.get_shield_power_unit_usage() + \
            self.get_engine_power_unit_usage() + \
            self.get_weapon_power_unit_usage() + \
            self.get_drone_power_unit_usage() + \
            self.get_specials_power_unit_usage()

    def get_shield_power_unit_usage(self):
        """
        :rtype: int
        :returns: The current shield system power usage in power units.
        """

        # TODO: Make this work.
        return 0

    def get_engine_power_unit_usage(self):
        """
        :rtype: int
        :returns: The current engine system power usage in power units.
        """

        # TODO: Make this work.
        return 0

    def get_weapon_power_unit_usage(self):
        """
        :rtype: int
        :returns: The current weapon system power usage in power units.
        """

        # TODO: Make this work.
        return 0

    def get_drone_power_unit_usage(self):
        """
        :rtype: int
        :returns: The current drone system power usage in power units.
        """

        # TODO: Make this work.
        return 0

    def get_specials_power_unit_usage(self):
        """
        :rtype: int
        :returns: The current special system power usage in power units.
        """

        # TODO: Make this work.
        return 0