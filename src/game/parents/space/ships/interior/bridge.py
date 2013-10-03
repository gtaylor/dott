from src.game.parents.space.hangar import HangarMixin
from src.game.parents.space.solar_system import SolarSystemPlaceObject
from src.daemons.server.commands.cmdtable import CommandTable
from src.daemons.server.commands.command import BaseCommand
from src.game.parents.space.ships.interior.base import SpaceShipInteriorObject
from src.daemons.server.commands.exceptions import CommandError
from src.daemons.server.objects.exceptions import NoSuchObject


class CmdLaunch(BaseCommand):
    """
    Launches the ship into space from a hangar.
    """

    name = 'launch'
    aliases = ['takeoff']

    #noinspection PyUnusedLocal
    def func(self, invoker, parsed_cmd):
        bridge = invoker.location
        ship = bridge.get_ship_obj()
        hangar = ship.location

        if not ship.is_ship_landed():
            raise CommandError("You're already flying around!")

        launch_to = hangar.get_launchto_location()
        if not launch_to:
            raise CommandError("The hangar your ship is in appears to be shut.")

        bridge.emit_to_contents("Starting launch sequence...")
        ship.start_launch_sequence()


#noinspection PyAttributeOutsideInit
class CmdDock(BaseCommand):
    """
    Either displays a list of dockable places, or docks if a destination is
    specified.
    """

    name = 'dock'
    aliases = ['land']

    #noinspection PyUnusedLocal
    def func(self, invoker, parsed_cmd):
        self.bridge = invoker.location
        self.ship = self.bridge.get_ship_obj()
        is_landed = self.ship.is_ship_landed()

        if is_landed:
            raise CommandError("You'll have to launch first!")

        self.solar_system = self.ship.get_solar_system_obj()

        if not parsed_cmd.arguments:
            # No arguments passed, show the places list.
            self.do_list_docks(invoker, parsed_cmd)
        else:
            # User provided input. Warping somewhere.
            self.do_dock(invoker, parsed_cmd)

    # noinspection PyUnusedLocal
    def do_list_docks(self, invoker, parsed_cmd):
        """
        The 'dock' command was invoked without arguments. This method
        renders the dockable locations list for the current location.
        """

        object_store = invoker.mud_service.object_store
        grouped_hangars, _ = self.ship.location.get_dockable_obj_list(self.ship)

        buf = self._get_header_str("Dockable Locations near %s" %
                                   self.ship.location.get_appearance_name(invoker))
        for inspace_obj_id, hangar_objs in grouped_hangars.items():
            inspace_obj = object_store.get_object(inspace_obj_id)
            buf += "\n {name}".format(
                name=inspace_obj.get_appearance_name(invoker),
            )
            for hangar_obj in hangar_objs:
                buf += "\n {id:>5}] {name}".format(
                    id=hangar_obj.id,
                    name=hangar_obj.get_appearance_name(invoker),
                )
        buf += self._get_footer_str()
        invoker.emit_to(buf)

    def do_dock(self, invoker, parsed_cmd):
        """
        An argument was provided with dock, meaning that the user wishes to
        dock.
        """

        object_store = invoker.mud_service.object_store

        try:
            dock_id = int(parsed_cmd.argument_string)
        except (TypeError, ValueError):
            raise CommandError('Invalid docking location ID.')

        _, flat_hangar_id_list = self.ship.location.get_dockable_obj_list(self.ship)
        if dock_id not in flat_hangar_id_list:
            raise CommandError('No dock with that ID found.')

        dock_obj = object_store.get_object(dock_id)
        invoker.emit_to('Docking in %s' % dock_obj.get_appearance_name(invoker))
        # TODO: Emit to others in system that ship is beginning to land/dock.
        self.ship.emit_to_interior(
            'A docking tone sounds as the ship begins its approach.'
        )
        # TODO: A CallLater based on ship maneuverability.
        # TODO: Emit to others in system that ship has landed.
        self.ship.move_to(dock_obj)
        self.ship.emit_to_interior(
            'A loud CLANG resonates through the hull as a docking collar '
            'is slapped on from outside.'
        )
        invoker.emit_to('You have docked in %s' % (
            dock_obj.get_appearance_name(invoker),
        ))
        # TODO: Emit to the place being docked in.


class CmdStatus(BaseCommand):
    """
    Shows a basic ship status display.
    """

    name = 'status'
    aliases = ['st']

    #noinspection PyUnusedLocal
    def func(self, invoker, parsed_cmd):
        bridge = invoker.location
        ship = bridge.get_ship_obj()
        solar_system = ship.get_solar_system_obj()

        is_landed = ship.is_ship_landed()
        ship_status = 'Landed' if is_landed else 'In flight'
        ship_location = solar_system.get_appearance_name(invoker)
        ship_id = '[%s]' % ship.id

        buf = self._get_footer_str() + "\n"
        buf += (
            "Ship Name: {ship_name:<22} ID: {ship_id:<7} Ship Type: {ship_type} ({ship_reference})\n"
            "State: {ship_status:<15} Ship Location: {ship_location}\n\n"
            " Shield: [======================] 100%"
            "   Hull: [======================] 100%"
        ).format(
            ship_name=ship.display_name,
            ship_id=ship_id,
            ship_type=ship.ship_type_name,
            ship_reference=ship.ship_reference,
            ship_status=ship_status,
            ship_location=ship_location,
        )
        buf += self._get_footer_str(pad_char='-')
        buf += '\n Reactor Utilization: 3 of 10 units'
        buf += '\n Shields: 1   Engines: 1   Weapons: 1   Drones: 1   Specials: 0'
        buf += self._get_footer_str()
        buf += '\n----- Weapon ----------- [##] Power --- Status ||--- Ammo Type ---- Rounds'
        buf += '\n {weapon_name:<23} [{weapon_num:>2}] 1 unit    {cycle_state:<6}'.format(
            weapon_num=1,
            weapon_name='Small Ion Cannon',
            cycle_state='Ready')
        buf += self._get_footer_str(pad_char='-')

        invoker.emit_to(buf)


class CmdContacts(BaseCommand):
    """
    Shows other objects in the same location in space.
    """

    name = 'contacts'
    aliases = ['con']

    #noinspection PyUnusedLocal
    def func(self, invoker, parsed_cmd):
        bridge = invoker.location
        ship = bridge.get_ship_obj()
        solar_system = ship.get_solar_system_obj()

        if ship.is_ship_landed():
            raise CommandError("What contacts? You aren't in space.")

        buf = self._get_header_str("Contacts near %s" % ship.location.get_appearance_name(invoker))
        for contact in ship.get_visible_contacts():
            buf += (
                "\n {id:>5}]{ship_class_code:<1}  {ship_reference:<10} "
                "{display_name:<20} S:[==========] H:[==========]  S:".format(
                id=contact.id,
                ship_class_code=contact.ship_class_code,
                ship_reference=contact.ship_reference,
                display_name=contact.display_name))
        buf += self._get_footer_str()

        invoker.emit_to(buf)


#noinspection PyAttributeOutsideInit
class CmdWarp(BaseCommand):
    """
    Either displays a list of warpable places, or warps to a place if a
    destination is specified.
    """

    name = 'warp'

    #noinspection PyUnusedLocal
    def func(self, invoker, parsed_cmd):
        self.bridge = invoker.location
        self.ship = self.bridge.get_ship_obj()
        self.current_place = self.ship.location
        is_landed = self.ship.is_ship_landed()

        if is_landed:
            raise CommandError("You'll have to launch first!")

        self.solar_system = self.ship.get_solar_system_obj()

        if not parsed_cmd.arguments:
            # No arguments passed, show the places list.
            self.do_list_places(invoker, parsed_cmd)
        else:
            # User provided input. Warping somewhere.
            self.do_warp_to(invoker, parsed_cmd)

    # noinspection PyUnusedLocal
    def do_list_places(self, invoker, parsed_cmd):
        """
        The 'warp' command was invoked without arguments. This method
        renders the warpable locations list for the system.
        """

        places = self.solar_system.get_places_obj_list()

        buf = self._get_header_str("Warpable Locations in %s" % self.solar_system.get_appearance_name(invoker))
        for place in places:
            buf += "\n {id:>5}] {name:<25} {marker}".format(
                marker='<-- You are here' if self.current_place.id == place.id else '  ',
                id=place.id,
                name=place.get_appearance_name(invoker),
            )
        buf += self._get_footer_str()
        invoker.emit_to(buf)

    def do_warp_to(self, invoker, parsed_cmd):
        """
        An argument was provided with warp, meaning that the user wishes to
        warp to a place.
        """

        service = invoker.mud_service

        try:
            warp_id = int(parsed_cmd.argument_string)
        except (TypeError, ValueError):
            raise CommandError('Invalid warp destination ID.')

        try:
            place_obj = service.object_store.get_object(warp_id)
        except NoSuchObject:
            raise CommandError('No warp destination with that ID found.')

        if place_obj.id == self.current_place.id:
            raise CommandError('You are already there!')

        if not isinstance(place_obj, SolarSystemPlaceObject):
            # Attempting to warp to a non-place.
            raise CommandError('No warp destination with that ID found.')

        if not self.solar_system == place_obj.get_solar_system_obj():
            # Attempting to warp to a place in another solar system.
            raise CommandError('No warp destination with that ID found.')

        invoker.emit_to('Warping to %s in the %s system.' % (
            place_obj.get_appearance_name(invoker),
            self.solar_system.get_appearance_name(invoker),
        ))
        self.ship.emit_to_interior(
            'The hull begins to vibrate, and the whine of the charging warp '
            'drives becomes deafening.'
        )
        # TODO: A CallLater based on ship maneuverability.
        self.ship.emit_to_interior(
            'The ship groans audibly as it flings itself into warp.'
        )
        # TODO: Move the ship somewhere unreachable.
        # TODO: CallLater to come out of warp.
        self.ship.move_to(place_obj)
        self.ship.emit_to_interior(
            'You feel a strong lurch as your vessel slows after its warp.'
        )
        invoker.emit_to('You arrive at %s in the %s system.' % (
            place_obj.get_appearance_name(invoker),
            self.solar_system.get_appearance_name(invoker),
        ))


class ShipBridgeCommandTable(CommandTable):
    commands = [
        CmdContacts(),
        CmdDock(),
        CmdLaunch(),
        CmdStatus(),
        CmdWarp(),
    ]


class SpaceShipBridgeObject(SpaceShipInteriorObject):
    """
    Ships are controlled from the bridge, regardless of size. Smaller ships
    call this a cockpit.
    """

    local_command_table = ShipBridgeCommandTable()

    def can_object_leave(self, obj):
        """
        Determine whether another object can leave this object.

        :param BaseObject obj: The object to check enter permissions for.
        :rtype: tuple
        :returns: A tuple in the format of ``(can_leave, message)``, where
            ``can_leave`` is a bool, and ``message`` is a string or ``None``,
            used to provide a reason for the object not being able to leave.
        """

        ship = self.get_ship_obj()
        ship_loc = ship.location
        is_landed = ship.is_ship_landed()

        if not is_landed or not ship_loc:
            return False, "Leave to space? Doesn't sound like a good idea..."

        # All is well
        return True, None

    def determine_leave_destination(self, obj):
        """
        Given an object that is going to leave this one, determine where said
        object will be moved to. This defaults to this object's location,
        but in the case of leaving a ship's bridge, they should end up outside
        the ship, rather than inside the ship object.

        :param BaseObject obj: The other object that is entering this one.
        :rtype: BaseObject
        :returns: The target location for the object to be moved to upon
            leaving this object.
        """

        ship = self.get_ship_obj()
        return ship.location