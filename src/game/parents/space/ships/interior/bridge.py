from src.game.parents.space.solar_system import SolarSystemPlaceObject
from src.server.commands.cmdtable import CommandTable
from src.server.commands.command import BaseCommand
from src.game.parents.space.ships.interior.base import SpaceShipInteriorObject
from src.server.commands.exceptions import CommandError
from src.server.objects.exceptions import InvalidObjectId

class CmdLaunch(BaseCommand):
    """
    Launches the ship into space from a hangar.
    """
    name = 'launch'

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

"""
      /@|
 ,-==/   ====[
(            [
 '-==\   ====[
      \@|

"""


class CmdStatus(BaseCommand):
    """
    Shows a basic ship status display.
    """
    name = 'status'

    #noinspection PyUnusedLocal
    def func(self, invoker, parsed_cmd):
        bridge = invoker.location
        ship = bridge.get_ship_obj()
        solar_system = ship.get_solar_system_obj()

        is_landed = ship.is_ship_landed()
        ship_status = 'Landed' if is_landed else 'In flight'
        ship_location = solar_system.get_appearance_name(invoker)
        ship_id = '[%s]' % ship.id

        retval = "Ship Name: {ship_name} ID: {ship_id} Ship Type: {ship_type} ({ship_class})\n" \
                 "State: {ship_status} Ship Location: {ship_location}\n\n" \
                 "  Armor: [=================     ] 80%\n" \
                 " Shield: [======================] 100%\n" \
                 "   Hull: [======================] 100%\n".format(
            ship_name='Implement me!'.ljust(30),
            ship_id = ship_id.ljust(10),
            ship_type=ship.ship_type_name,
            ship_class=ship.ship_class,
            ship_status=ship_status.ljust(15),
            ship_location=ship_location,
        )

        invoker.emit_to(retval)


class CmdWarp(BaseCommand):
    """
    Either displays a list of warpable places, or warps to a place
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

    def do_list_places(self, invoker, parsed_cmd):
        """
        The 'warp' command was invoked without arguments. This method
        renders the warpable locations list for the system.
        """
        places = self.solar_system.get_places_obj_list()

        buffer = "Warpable Locations -- %s\n" % (
            self.solar_system.get_appearance_name(invoker),
        )
        buffer += '-' * 78
        for place in places:
            buffer += "\n %s %s] %s" % (
                '>>' if self.current_place.id == place.id else '  ',
                place.id.rjust(5),
                place.get_appearance_name(invoker),
            )
        buffer += '\n'
        buffer += '-' * 78
        invoker.emit_to(buffer)

    def do_warp_to(self, invoker, parsed_cmd):
        """
        An argument was provided with warp, meaning that the user wishes to
        warp to a place.
        """
        service = invoker._mud_service
        # Join all arguments together into one single string so we can
        # do a contextual search for the whole thing.
        full_arg_str = ' '.join(parsed_cmd.arguments)

        try:
            place_obj = service.object_store.get_object(full_arg_str)
        except InvalidObjectId:
            raise CommandError('No warp destination with that ID found.')

        if not isinstance(place_obj, SolarSystemPlaceObject):
            # Attempting to warp to a non-place.
            raise CommandError('No warp destination with that ID found.')

        if not self.solar_system == place_obj.get_solar_system_obj():
            # Attempting to warp to a place in another solar system.
            raise CommandError('No warp destination with that ID found.')

        invoker.emit_to('Warping to %s' % (
            place_obj.get_appearance_name(invoker),
        ))
        self.ship.emit_to_interior(
            'The hull begins to vibrate, and the whine of the charging warp' \
            'drives becomes deafening.'
        )
        # TODO: A CallLater based on ship manueverabiliy.
        self.ship.emit_to_interior(
            'The ship groans audibly as it flings itself into warp.'
        )
        # TODO: Move the ship somewhere unreachable.
        # TODO: CallLater to come out of warp.
        self.ship.move_to(place_obj)
        self.ship.emit_to_interior(
            'You feel a strong lurch as your vessel slows after its warp.'
        )


class ShipBridgeCommandTable(CommandTable):
    commands = [
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
