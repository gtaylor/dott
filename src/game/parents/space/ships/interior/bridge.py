from src.server.commands.cmdtable import CommandTable
from src.server.commands.command import BaseCommand
from src.game.parents.space.ships.interior.base import SpaceShipInteriorObject
from src.server.commands.exceptions import CommandError

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


class ShipBridgeCommandTable(CommandTable):
    commands = [
        CmdLaunch(),
        CmdStatus(),
    ]


class SpaceShipBridgeObject(SpaceShipInteriorObject):
    """
    Ships are controlled from the bridge, regardless of size. Smaller ships
    call this a cockpit.
    """
    local_command_table = ShipBridgeCommandTable()
